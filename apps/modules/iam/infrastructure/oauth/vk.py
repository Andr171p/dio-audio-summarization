from typing import Literal, NotRequired, TypedDict

import base64
import hashlib
import logging
import secrets

import aiohttp

from ...application.exceptions import OAuthError

logger = logging.getLogger(__name__)


class AuthorizationData(TypedDict):
    """Данные для инициации авторизации пользователя через ВК"""

    authorization_url: str
    code_verifier: str
    state: str


class Tokens(TypedDict):
    """Набор токенов"""

    access_token: str
    refresh_token: str
    id_token: str
    token_type: str
    expires_in: int
    user_id: int | str
    state: str
    scope: str


class PublicInfo(TypedDict):
    """Публичная информация о пользователе"""

    user_id: str | int
    first_name: str
    last_name: str
    phone: str
    avatar: str
    email: str


class UserInfo(TypedDict):
    """Персональная информация о пользователе

    Attributes:
        user_id: Идентификатор пользователя в ВК, пример: '1234567890'
        first_name: Имя пользователя, пример: 'Ivan'
        last_name: Фамилия пользователя, пример: 'Ivanov'
        avatar: Ссылка на фото профиля
        sex: Пол пользователя, где 1 - женский, 2 - мужской, 0 - пол не указан
        verified: Статус верификации пользователя
        birthday: Дата рождения пользователя, пример: '01.01.2000'
        phone: Номер телефона пользователя (если запрошен через scope)
        email: Адрес электронной почты (если запрошен через scope)
    """

    user_id: str | int
    first_name: str
    last_name: str
    avatar: str
    sex: Literal[0, 1, 2]
    verified: bool
    birthday: str
    phone: NotRequired[str]
    email: NotRequired[str]


def generate_pkce_params() -> tuple[str, str]:
    """Генерация code_verifier и code_challenge"""

    # Генерация случайного code_verifier (43-128 символов)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    # Создание code_challenge методом S256
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


class VKOAuthClient:
    def __init__(
            self,
            client_id: str,
            base_url: str,
            redirect_uri: str,
            scope: str = "email phone",
    ) -> None:
        self._client_id = client_id
        self._base_url = base_url
        self._redirect_uri = redirect_uri
        self._scope = scope

    async def generate_authorization_url(self) -> AuthorizationData:
        """Инициация ВК OAuth 2.0 authorization flow,
        генерирует URL для авторизации пользователя используя его ВК аккаунт.
        """

        # Генерация PKCE параметров
        code_verifier, code_challenge = generate_pkce_params()
        # Генерация state для защиты от CSRF
        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": self._scope,
            "state": state,
        }
        try:
            logger.debug("Initiate VK OAuth 2.0 authorization flow")
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.get(
                url="/authorize", params=params, allow_redirects=False
            ) as response:
                response.raise_for_status()
                return {
                    "authorization_url": f"{response.url}",
                    "code_verifier": code_verifier,
                    "state": state,
                }
        except aiohttp.ClientResponseError as e:
            error_message = (
                "Error occurred while authorization URL generation, "
                f"status: {e.status}, "
                f"message: {e.message}"
            )
            logger.exception(error_message)
            raise OAuthError(error_message, code="VK_AUTHORIZATION_URL_GENERATION_FAILED") from e

    async def get_tokens(
            self, authorization_code: str, code_verifier: str, state: str, device_id: str
    ) -> Tokens:
        """Получение токенов пользователя"""

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "code": authorization_code,
            "code_verifier": code_verifier,
            "device_id": device_id,
            "state": state,
        }
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.post(
                url="oauth2/auth", headers=headers, data=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            error_message = (
                "Error occurred while receiving tokens, "
                f"status: {e.status}, message: {e.message}"
            )
            logger.exception(error_message)
            raise OAuthError(error_message, code="VK_TOKEN_RECEIVING_FAILED") from e

    async def get_public_info(self, id_token: str) -> PublicInfo:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {"client_id": self._client_id, "id_token": id_token}
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.post(
                url="oauth2/public_info", headers=headers, data=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return data["user"]
        except aiohttp.ClientResponseError as e:
            error_message = (
                "Error occurred while receiving user public info, "
                f"status: {e.status}, "
                f"message: {e.message}"
            )
            logger.exception(error_message)
            raise OAuthError(error_message, code="VK_PUBLIC_INFO_RECEIVING_FAILED") from e

    async def get_userinfo(self, access_token: str) -> UserInfo:
        """Получение информации о пользователе

        :param access_token: ACCESS токен полученный методом `get_tokens`
        :returns: Запрашиваемая информация о пользователе
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {"client_id": self._client_id, "access_token": access_token}
        try:
            logger.debug("User info is requested")
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.post(
                url="/user_info", headers=headers, data=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["user"]
        except aiohttp.ClientResponseError as e:
            error_message = (
                "Error occurred while receiving user personal info, "
                f"status: {e.status}, "
                f"message: {e.message}"
            )
            logger.exception(error_message)
            raise OAuthError(error_message, code="VK_USER_INFO_RECEIVING_FAILED") from e
