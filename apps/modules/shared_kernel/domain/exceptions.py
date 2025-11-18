from typing import Any

from abc import ABC
from enum import StrEnum


class ErrorType(StrEnum):
    """Тип доменной ошибки"""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    PRECONDITION_FAILED = "precondition_failed"
    INVARIANT_VIOLATION = "invariant_violation"
    EXTERNAL_DEPENDENCY_ERROR = "external_dependency_error"
    UNKNOWN = "unknown"


class AppError(Exception, ABC):
    """Базовое исключение приложения (самый верхний уровень)"""

    def __init__(
            self,
            message: str,
            type: ErrorType,  # noqa: A002
            code: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        """
        :param message: Человеко-читаемое сообщение
        :param code: Краткое описание ошибки, например: `USER_NOT_FOUND`, `UPLOAD_FAILED`, ...
        :param details: Дополнительные детали
        :param original_error: Оригинальный класс ошибки
        """
        self.message = message
        self.type = type
        self.code = code
        self.details = details or {}
        self.original_error = original_error
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Преобразование в словарь для API responses"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
