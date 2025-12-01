from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class UnsupportedAudioError(AppError):
    """Неподдерживаемый аудио файл"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.VALIDATION_ERROR,
            code="UNSUPPORTED_AUDIO",
            details=details
        )
