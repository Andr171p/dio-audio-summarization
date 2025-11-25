from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class AlreadyRegisteredError(AppError):
    """Пользователь уже зарегистрирован"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.CONFLICT,
            code="USER_ALREADY_REGISTERED",
            details=details,
        )


class UnauthorizedError(AppError):
    """Ошибка авторизации"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.UNAUTHORIZED,
            code="UNAUTHORIZED",
            details=details,
        )


class OAuthSecurityError(AppError):
    pass


class InvalidStateError(OAuthSecurityError):
    """Неверный state сессии авторизации"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message, type=ErrorType.VALIDATION_ERROR, code="INVALID_STATE", details=details
        )
