from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


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
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
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
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
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
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="REMOVING_FAILED",
            details=details,
            original_error=original_error
        )
