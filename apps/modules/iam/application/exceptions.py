from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class NoLongerGuestError(AppError):
    """Пользователь больше не является гостем"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.NOT_FOUND,
            code="USER_IS_NO_LONGER_GUEST",
            details=details
        )


class AlreadyRegisteredError(AppError):
    """Пользователь уже зарегистрирован"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.CONFLICT,
            code="USER_ALREADY_REGISTERED",
            details=details,
        )


class RegistrationRequiredError(AppError):
    """Требуется регистрация"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.NOT_FOUND,
            code="REGISTRATION_REQUIRED",
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


class OAuthError(AppError):
    """Базовая ошибка при использовании OAuth провайдера"""

    def __init__(self, message: str, code: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message, type=ErrorType.EXTERNAL_DEPENDENCY_ERROR, code=code, details=details
        )


class InvalidPKCEError(OAuthError):
    """Неверный state сессии авторизации"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.VALIDATION_ERROR,
            code="INVALID_PKCE_PARAMS",
            details=details
        )
