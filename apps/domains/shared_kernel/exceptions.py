from typing import Any

from abc import ABC


class AppError(Exception, ABC):
    """Базовое исключение приложения (самый верхний уровень)"""

    def __init__(
            self,
            message: str,
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


class UploadingFailedError(AppError):
    """Ошибка загрузки файла в хранилище"""

    def __init__(
            self,
            message: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="UPLOADING_FAILED",
            details=details,
            original_error=original_error
        )


class DownloadFailedError(AppError):
    """Ошибка при скачивании файла из хранилища"""

    def __init__(
            self,
            message: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="DOWNLOAD_FAILED",
            details=details,
            original_error=original_error
        )


class RemovingFailedError(AppError):
    """Ошибка при удалении файла"""

    def __init__(
            self,
            message: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="REMOVING_FAILED",
            details=details,
            original_error=original_error
        )
