from typing import Any, Self, overload

from uuid import UUID

from pydantic import EmailStr, Field

from config.dev import settings
from modules.shared_kernel.domain import AggregateRoot, Entity

from ..utils.security import hash_secret, verify_secret
from .events import UserRegisteredEvent
from .exceptions import InvalidCredentialsError, UserNotEnabledError
from .value_objects import (
    AuthProvider,
    CredentialsRegistration,
    HashedUserCredentials,
    ProfileInfo,
    SocialAccountRegistration,
    UserCredentials,
    UserRole,
    UserStatus,
)


class SocialAccount(Entity):
    provider: AuthProvider
    user_id: UUID
    profile_info: ProfileInfo

    @property
    def email(self) -> EmailStr | None:
        return self.profile_info.get("email")


class User(AggregateRoot):
    email: EmailStr | None = None
    username: str
    role: UserRole
    status: UserStatus
    credentials: HashedUserCredentials | None = None
    social_accounts: list[SocialAccount] = Field(default_factory=list)
    auth_providers: set[AuthProvider] = Field(default_factory=set)

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
        return self.status != UserStatus.PENDING

    def repeat_email_verification(self) -> None:
        """Повторение отправки письма для верификации email"""
        self._register_event(
            UserRegisteredEvent(user_id=self.id, user_status=self.status, email=self.email)
        )

    @overload
    @classmethod
    def register(cls, registration: CredentialsRegistration) -> Self:
        user = cls(
            email=registration.email,
            username=registration.username,
            role=UserRole.GUEST,
            status=UserStatus.PENDING,
            credentials=HashedUserCredentials(
                email=registration.email, password_hash=hash_secret(registration.password)
            ),
            auth_providers={AuthProvider.CREDENTIALS}
        )
        cls._register_event(
            user, UserRegisteredEvent(user_id=user.id, user_status=user.status, email=user.email)
        )
        return user

    @overload
    @classmethod
    def register(cls, registration: SocialAccountRegistration) -> Self: pass

    def register(
            self, registration: CredentialsRegistration | SocialAccountRegistration
    ) -> Self: ...

    def authenticate_by_credentials(self, credentials: UserCredentials) -> Self:
        if self.status in {UserStatus.BANNED, UserStatus.DELETED}:
            raise UserNotEnabledError(
                user_status=self.status,
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        if not verify_secret(credentials.password, self.credentials.password_hash):
            raise InvalidCredentialsError(
                "Invalid password!",
                details={"user_id": self.id, "email": self.email, "username": self.username}
            )
        return self


class Admin(User):
    role: UserRole = Field(default=UserRole.ADMIN)
