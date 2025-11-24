from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class EmailSendingError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="EMAIL_SENDING_FAILED",
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            details=details
        )
