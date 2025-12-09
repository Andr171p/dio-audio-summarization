from typing import Any

import logging
from datetime import timedelta

from config.dev import settings
from modules.shared_kernel.application import KeyValueCache, MessageBus, UnitOfWork

from ..domain import (
    AuthProvider,
    Guest,
    SocialAccount,
    Token,
    TokenPair,
    TokenType,
    User,
    UserClaims,
    UserCredentials,
    UserRole,
)
from ..domain.exceptions import InvalidTokenError, TokenExpiredError
from ..infrastructure.oauth import vk_oauth_client
from ..utils.common import expires_at
from ..utils.security import decode_token, issue_token
from .dto import GuestToken, InitiatedOAuthFlow, PKCESession, VKCallback
from .exceptions import (
    AlreadyRegisteredError,
    InvalidPKCEError,
    NoLongerGuestError,
    RegistrationRequiredError,
    UnauthorizedError,
)
from .queries import GetGuestQuery
from .repositories import UserRepository

logger = logging.getLogger(__name__)


def generate_token_pair(payload: dict[str, Any]) -> TokenPair:
    """Генерирует пару JWT токенов (access и refresh)

    :param payload: Полезная нагрузка для JWT.
    :return: Объект с access/refresh и прочими метаданными.
    """
    access_token_expires_in = timedelta(minutes=settings.jwt.user_access_token_expires_in_minutes)
    refresh_token_expires_in = timedelta(days=settings.jwt.user_refresh_token_expires_in_days)
    access_token = issue_token(
        token_type=TokenType.ACCESS,
        payload=payload,
        expires_in=access_token_expires_in,
    )
    refresh_token = issue_token(
        token_type=TokenType.REFRESH,
        payload=payload,
        expires_in=refresh_token_expires_in
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at(access_token_expires_in),
    )


def generate_access_token(payload: dict[str, Any]) -> Token:
    """Генерирует access токен

    :param payload: Полезная нагрузка которую нужно передать в токен
    :returns: Объект с access токенов и его временем истечения в формате timestamp
    """
    expires_in = timedelta(days=settings.jwt.guest_access_token_expires_in_days)
    access_token = issue_token(
        token_type=TokenType.ACCESS, payload=payload
    )
    return Token(access_token=access_token, expires_at=expires_at(expires_in))


def verify_token(token: str) -> UserClaims:
    """Верификация токена пользователя"""
    try:
        payload = decode_token(token)
    except TokenExpiredError as e:
        return UserClaims(active=False, cause=f"{e}")
    except InvalidTokenError as e:
        error_message = f"Token verification failed with error: {e}"
        logger.exception(error_message)
        raise UnauthorizedError(error_message) from e
    return UserClaims.model_validate({"active": True, **payload})


class GuestService:
    def __init__(self, uow: UnitOfWork, repository: UserRepository) -> None:
        self._uow = uow
        self._repository = repository

    async def _create_new(self, device_id: str | None = None) -> GuestToken:
        """Создание нового гостя

        :param device_id: Идентификатор устройства, полученный с клиента.
        :returns: Гостевой токен.
        """

        async with self._uow as uow:
            guest = Guest.create(device_id)
            created_guest = await self._repository.create(guest)
            await uow.commit()
        payload = created_guest.to_jwt_payload()
        token = generate_access_token(payload)
        return GuestToken(
            guest_id=created_guest.id,
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at,
        )

    async def get_or_create(self, query: GetGuestQuery) -> GuestToken:
        if query.guest_id is None:
            return await self._create_new(query.device_id)
        guest = await self._repository.read(query.guest_id)
        if guest is None:
            # Создание гостя если гость не был найден
            return await self._create_new(query.device_id)
        if guest.is_expired:
            # Если гостевой доступ истёк, то создаётся новый
            async with self._uow as uow:
                await self._repository.delete(guest.id)
                await uow.commit()
                return await self._create_new(query.device_id)
        if guest.role != UserRole.GUEST:
            # Пользователь теперь зарегистрирован (больше не гость)
            raise NoLongerGuestError(
                f"User `{guest.username}` is no longer a guest!",
                details={"user_id": guest.id, "role": guest.role, "status": guest.status}
            )
        payload = guest.to_jwt_payload()
        token = generate_access_token(payload)
        return GuestToken(
            guest_id=guest.id,
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at,
        )


class CredentialsAuthService:
    """Сервис для аутентификации пользователей через учётные данные"""

    def __init__(
            self, uow: UnitOfWork, repository: UserRepository, message_bus: MessageBus
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._message_bus = message_bus

    async def register(self, credentials: UserCredentials) -> User:
        async with self._uow.transactional() as uow:
            user = await self._repository.get_by_email(credentials.email)
            if user is None:
                user = User.register_by_credentials(credentials)
                await self._repository.create(user)
            elif user is not None and not user.is_registration_completed():
                logger.info(
                    "Repeat email verification for %s user with email `%s` "
                    "and current status `%s`",
                    user.id, user.email, user.status
                )
                user.repeat_email_verification()
            else:
                raise AlreadyRegisteredError(
                    f"User with email {user.email} already registered",
                    details={"email": user.email, "username": user.username}
                )
            await uow.commit()
            for event in user.collect_events():
                await self._message_bus.send(event)
            return user

    async def authenticate(self, credentials: UserCredentials) -> TokenPair:
        logger.debug(
            "Start authentication by credentials for user with email %s", credentials.email
        )
        user = await self._repository.get_by_email(credentials.email)
        if user is None:
            raise RegistrationRequiredError(
                "Complete registration to continue",
                details={"provider": "credentials", "email": credentials.email}
            )
        authed_user = user.authenticate_by_credentials(credentials)
        payload = authed_user.to_jwt_payload()
        token_pair = generate_token_pair(payload)
        logger.info(
            "User %s, email %s successfully authenticated", authed_user.id, authed_user.email
        )
        return token_pair


class VKAuthService:
    def __init__(
            self,
            uow: UnitOfWork,
            repository: UserRepository,
            cache: KeyValueCache[PKCESession],
            message_bus: MessageBus
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._cache = cache
        self._message_bus = message_bus

    async def init_oauth_flow(self) -> InitiatedOAuthFlow:
        """Инициация OAuth 2.0 потока.

        :returns: URL адрес для авторизации пользователя через ВК + идентификатор PKCE сессии.

        Примечание: рекомендуемо сохранять идентификатор PKCE сессии в Cookie.
        """

        auth_data = await vk_oauth_client.generate_authorization_url()
        pkce_session = PKCESession(
            code_verifier=auth_data["code_verifier"], state=auth_data["state"]
        )
        pkce_session_id = str(pkce_session.session_id)
        await self._cache.set(pkce_session_id, pkce_session)
        return InitiatedOAuthFlow(
            authorization_url=auth_data["authorization_url"], pkce_session_id=pkce_session_id
        )

    async def _handle_callback(self, pkce_session_id: str, callback: VKCallback) -> dict[str, Any]:
        """Обработка callback данных после авторизации пользователя через ВК.

        :param pkce_session_id: Идентификатор PKCE сессии.
        :param callback: Callback после авторизации.
        :returns: Информация об ВК аккаунте пользователя.
        :raises InvalidPKCEError - при несоответствии PKCE параметров.
        """

        if not pkce_session_id:
            raise InvalidPKCEError("Session is missing!")
        pkce_session = await self._cache.get(pkce_session_id)
        if pkce_session is None:
            raise InvalidPKCEError("Session expired or invalid!")
        if pkce_session.state != callback.state:
            await self._cache.invalidate(pkce_session_id)
            raise InvalidPKCEError("Invalid state parameter!")
        tokens = await vk_oauth_client.get_tokens(
            authorization_code=callback.authorization_code,
            code_verifier=pkce_session.code_verifier,
            state=callback.state,
            device_id=callback.device_id,
        )
        return await vk_oauth_client.get_userinfo(tokens["access_token"])

    async def register(self, pkce_session_id: str, callback: VKCallback) -> User:
        userinfo = await self._handle_callback(pkce_session_id, callback)
        user_id = userinfo["user_id"]
        async with self._uow.transactional() as uow:
            user = await self._repository.get_by_social_account(AuthProvider.VK, user_id)
            if user is not None:
                raise AlreadyRegisteredError(
                    f"User already registered by VK, user_id {user_id}",
                    details={
                        "email": userinfo.get("email"),
                        "first_name": userinfo.get("first_name"),
                        "last_name": userinfo.get("last_name"),
                    }
                )
            social_account = SocialAccount.create(
                provider=AuthProvider.VK, social_user_id=userinfo["user_id"], **userinfo
            )
            user = User.register_by_social_account(social_account)
            await self._repository.create(user)
            await uow.commit()
        for event in user.collect_events():
            await self._message_bus.send(event)
        return user

    async def authenticate(self, pkce_session_id: str, callback: VKCallback) -> TokenPair:
        """Аутентифицирует пользователя.

        :param pkce_session_id: Идентификатор PKCE сессии.
        :param callback: Callback после авторизации через ВК.
        :returns: Пара токенов access + refresh
        """

        userinfo = await self._handle_callback(pkce_session_id, callback)
        user = await self._repository.get_by_social_account(AuthProvider.VK, userinfo["user_id"])
        if user is None:
            raise RegistrationRequiredError(
                "Complete registration to continue",
                details={"provider": "VK", "user_id": userinfo["user_id"]}
            )
        payload = user.to_jwt_payload()
        return generate_token_pair(payload)
