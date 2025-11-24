from typing import NotRequired, TypedDict

from enum import StrEnum
from uuid import UUID

from pydantic import EmailStr, HttpUrl

from modules.shared_kernel.domain import ValueObject


class UserStatus(StrEnum):
    """Статус пользователя в системе

    Attributes:
        PENDING_EMAIL_VERIFICATION: Зарегистрирован через credentials, пока не подтвердил email.
        EMAIL_VERIFIED: Подтверждён email
        (автоматически устанавливается при регистрации через социальные сети)
        BANNED: Бан пользователя (ограничение действий)
        DELETED: Пользователь был удалён
    """

    PENDING_EMAIL_VERIFICATION = "pending"
    EMAIL_VERIFIED = "email_verified"
    BANNED = "banned"
    DELETED = "deleted"


class UserCredentials(ValueObject):
    """Учетные данные пользователя"""

    username: str
    email: EmailStr
    password: str


class HashedUserCredentials(ValueObject):
    email: EmailStr
    password_hash: str


class UserRole(StrEnum):
    """Системные пользовательские роли.

    Attributes:
        SUPERADMIN: Полный доступ ко всей системе.
        ADMIN: Администратор с ограниченными правами
        MANAGER: Менеджер (управление пользователями/контентом).
        MODERATOR: # Модератор (модерация контента).
        USER: Обычный зарегистрированный пользователь.
        GUEST: Пользователь с неподтверждённым email.
    """

    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class ProfileInfo(TypedDict):
    user_id: str
    email: NotRequired[EmailStr]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    avatar_url: NotRequired[HttpUrl]


class AuthProvider(StrEnum):
    """Возможные провайдеры для регистрации и аутентификации пользователей"""

    CREDENTIALS = "credentials"
    VK = "VK"
    Yandex = "Yandex"
    MAX = "Max"
    GOSUSLUGI = "Gosuslugi"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPair(ValueObject):
    access_token: str
    refresh_token: str
    expires_at: int


class JWTClaims(ValueObject):
    """Базовая модель для интроспекции JWT"""

    active: bool = False
    cause: str | None = None
    token_type: TokenType | None = None
    iss: HttpUrl | None = None
    sub: str | None = None
    aud: str | None = None
    exp: int | float | None = None
    iat: int | float | None = None
    jti: UUID | None = None


class UserClaims(JWTClaims):
    username: str | None = None
    email: EmailStr | None = None
    status: UserStatus | None = None
