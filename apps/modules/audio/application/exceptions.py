from typing import Any

from uuid import UUID

from modules.shared_kernel.application.exceptions import NotFoundError


class AudioCollectionNotFoundError(NotFoundError):
    def __init__(self, collection_id: UUID, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=f"Audio collection not found by id {collection_id}",
            code="AUDIO_COLLECTION_NOT_FOUND",
            details=details
        )
