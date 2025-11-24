from typing import Any, Self, overload

from uuid import UUID

from pydantic import EmailStr, Field, model_validator

from config.dev import settings
from modules.shared_kernel.domain import Entity, InvariantViolationError

from ..utils.security import hash_secret, verify_secret
from .events import UserRegisteredEvent
from .exceptions import InvalidCredentialsError, UserNotEnabledError
from .value_objects import (
    AuthProvider,
    ProfileInfo,
    UserCredentials,
    UserRole,
    UserStatus,
)


class SocialAccount(Entity):
    """Аккаунт пользователя у стороннего провайдера.

    Attributes:
        provider: Тип провайдера аутентификации.
        user_id: Идентификатор пользователя у внешнего провайдера.
        profile_info: Дополнительная информация об аккаунте.
    """

    provider: AuthProvider
    user_id: UUID
    profile_info: ProfileInfo

    @property
    def email(self) -> EmailStr | None:
        return self.profile_info.get("email")


class User(Entity):
    email: EmailStr | None = None
    username: str
    role: UserRole
    status: UserStatus
    password_hash: str | None = None
    social_accounts: list[SocialAccount] = Field(default_factory=list)
    auth_providers: set[AuthProvider] = Field(default_factory=set)

    @model_validator(mode="after")
    def _validate_invariant(self) -> Self:
        """Валидация инвариантов"""
        has_email, has_password_hash = self.email is not None, self.password_hash is not None
        if AuthProvider.CREDENTIALS in self.auth_providers:
            if not has_email:
                raise InvariantViolationError(
                    "Email is required for credentials authentication",
                    entity_name=self.__class__.__name__,
                    details={
                        "user_id": self.id,
                        "status": self.status,
                        "auth_providers": self.auth_providers
                    },
                )
            if not has_password_hash:
                raise InvariantViolationError(
                    "Password is required for credentials authentication",
                    entity_name=self.__class__.__name__,
                    details={"user_id": self.id, "status": self.status, "email": self.email},
                )
        return self

    def to_jwt_payload(self, **kwargs) -> dict[str, Any]:
        """Получение полезной нагрузки для JWT"""
        return {
            "iss": settings.app.url,
            "sub": self.id,
            "username": self.username,
            "email": self.email,
            "status": self.status,
            "role": self.role,
            **kwargs,
        }

    def is_registration_completed(self) -> bool:
        """Завершена ли регистрация успешно"""
        return self.status != UserStatus.PENDING_EMAIL_VERIFICATION

    def repeat_email_verification(self) -> None:
        """Повторение отправки письма для верификации email"""
        self._register_event(
            UserRegisteredEvent(user_id=self.id, user_status=self.status, email=self.email)
        )

    @overload
    @classmethod
    def register(cls, credentials: UserCredentials) -> Self:
        user = cls(
            email=credentials.email,
            username=credentials.username,
            role=UserRole.GUEST,
            status=UserStatus.PENDING_EMAIL_VERIFICATION,
            password_hash=hash_secret(credentials.password),
            auth_providers={AuthProvider.CREDENTIALS}
        )
        cls._register_event(
            user, UserRegisteredEvent(user_id=user.id, user_status=user.status, email=user.email)
        )
        return user

    @overload
    @classmethod
    def register(cls, social_account: SocialAccount) -> Self: pass

    def register(
            self, registration: UserCredentials | SocialAccount
    ) -> Self: ...

    def authenticate_by_credentials(self, credentials: UserCredentials) -> Self:
        if self.status in {UserStatus.BANNED, UserStatus.DELETED}:
            raise UserNotEnabledError(
                user_status=self.status,
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        if not verify_secret(credentials.password, self.password_hash):
            raise InvalidCredentialsError(
                "Invalid password!",
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        return self


class Admin(User):
    role: UserRole = Field(default=UserRole.ADMIN)
