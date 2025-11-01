from domains.shared_kernel.domain import DomainError


class AudioCollectionNotFoundError(DomainError):
    """Не найдена аудио-коллекция"""

    def __init__(
            self,
            message: str = "Audio collection not found",
            code: str = "AUDIO_COLLECTION_NOT_FOUND",
    ) -> None:
        super().__init__(message, code)
