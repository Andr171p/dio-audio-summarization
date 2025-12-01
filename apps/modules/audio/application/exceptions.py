from typing import Any

from modules.shared_kernel.domain import AppError, ErrorType


class AudioSplittingError(AppError):
    """Ошибка при разделении аудио на чанки"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            type=ErrorType.EXTERNAL_DEPENDENCY_ERROR,
            code="AUDIO_SPLITTING_FAILED",
            details=details
        )
