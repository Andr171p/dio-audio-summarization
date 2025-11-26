from typing import Any

import logging
from datetime import timedelta

from config.dev import settings

from ..domain import (
    AuthProvider,
    SocialAccount,
    TokenPair,
    TokenType,
    User,
    UserClaims,
    UserCredentials,
)
from ..domain.exceptions import InvalidTokenError, TokenExpiredError
from ..infrastructure.oauth import vk_oauth_client
from ..utils.common import expires_at
from ..utils.security import decode_token, issue_token
from .dto import PKCESession, VKCallback
from .exceptions import InvalidPKCEError, UnauthorizedError
from .repositories import UserRepository

logger = logging.getLogger(__name__)


def generate_token_pair(payload: dict[str, Any]) -> TokenPair:
    """Генерирует пару JWT токенов (access и refresh)

    :param payload: Полезная нагрузка для JWT
    :return: Объект с access/refresh и прочими метаданными.
    """
    access_token = issue_token(
        token_type=TokenType.ACCESS,
        payload=payload,
        expires_in=timedelta(minutes=settings.jwt.access_token_expires_in_minutes)
    )
    refresh_token = issue_token(
        token_type=TokenType.REFRESH,
        payload=payload,
        expires_in=timedelta(days=settings.jwt.refresh_token_expires_in_days)
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at(timedelta(minutes=settings.jwt.access_token_expires_in_minutes))
    )


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


class CredentialsAuthNService:
    """Сервис для аутентификации пользователей через учётные данные"""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def authenticate(self, credentials: UserCredentials) -> TokenPair:
        logger.debug(
            "Start authentication by credentials for user with email %s", credentials.email
        )
        user = await self._repository.get_by_email(credentials.email)
        authed_user = user.authenticate_by_credentials(credentials)
        payload = authed_user.to_jwt_payload()
        token_pair = generate_token_pair(payload)
        logger.info(
            "User %s, email %s successfully authenticated", authed_user.id, authed_user.email
        )
        return token_pair


class VKAuthNService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def register(self, callback: VKCallback, session: PKCESession) -> ...:
        if callback.state != session.state:
            raise InvalidPKCEError("Invalid auth session state!")
        tokens = await vk_oauth_client.get_tokens(
            authorization_code=callback.authorization_code,
            code_verifier=session.code_verifier,
            state=callback.state,
            device_id=callback.device_id,
        )
        userinfo = await vk_oauth_client.get_userinfo(tokens["access_token"])
        social_account = SocialAccount.create(
            provider=AuthProvider.VK, user_id=userinfo["user_id"], **userinfo
        )
        user = User.register_by_social_account(social_account)
        await self._repository.create(user)

    async def authenticate(self, callback: VKCallback, session: PKCESession) -> TokenPair:
        if callback.state != session.state:
            raise InvalidPKCEError("Invalid auth session state!")
        tokens = await vk_oauth_client.get_tokens(
            authorization_code=callback.authorization_code,
            code_verifier=session.code_verifier,
            state=callback.state,
            device_id=callback.device_id,
        )
        userinfo = await vk_oauth_client.get_userinfo(tokens["access_token"])
        user = await self._repository.get_by_social_account(AuthProvider.VK, userinfo["user_id"])
        payload = user.to_jwt_payload()
        return generate_token_pair(payload)
