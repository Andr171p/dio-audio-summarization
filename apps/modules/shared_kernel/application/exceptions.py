from typing import Any

from uuid import UUID

from ..domain import AppError


class NotFoundError(AppError):
    pass


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


class DuplicateError(AppError):
    """Дублирование сущности"""

    def __init__(
            self,
            entity_name: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None,
    ) -> None:
        super().__init__(
            message=f"{entity_name} already exists",
            code="DUPLICATE_ENTITY",
            details=details,
            original_error=original_error
        )


class CreationError(AppError):
    """Ошибка при создании записи в ресурса"""

    def __init__(
            self,
            entity_name: str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while {entity_name} creation",
            code="CREATION_FAILED",
            details=details,
            original_error=original_error
        )


class ReadingError(AppError):
    """Ошибка при чтении данных"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while reading {entity_name} by {entity_id}",
            code="READING_FAILED",
            details=details,
            original_error=original_error
        )


class UpdateError(AppError):
    """Ошибка при обновлении ресурса"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while update {entity_name} by {entity_id}",
            code="UPDATE_FAILED",
            details=details,
            original_error=original_error
        )


class DeleteError(AppError):
    """Ошибка при удалении ресурса"""

    def __init__(
            self,
            entity_name: str,
            entity_id: UUID | str,
            details: dict[str, Any] | None = None,
            original_error: Exception | None = None
    ) -> None:
        super().__init__(
            message=f"Error occurred while delete {entity_name} by {entity_id}",
            code="DELETE_FAILED",
            details=details,
            original_error=original_error
        )
