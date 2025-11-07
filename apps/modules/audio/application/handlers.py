from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.summarization.domain import SummarizationStartedEvent

import asyncio

from modules.shared_kernel.application import Storage

from .repository import CollectionRepository


class SummarizationStartedHandler:
    def __init__(
            self, repository: CollectionRepository, storage: Storage
    ) -> None:
        self.repository = repository
        self.storage = storage

    async def handle(self, event: "SummarizationStartedEvent") -> None:
        collection = await self.repository.read(event.collection_id)
        presigned_urls: list[str] = await asyncio.gather(
            *[
                self.storage.generate_presigned_url(record.filepath)
                for record in collection.records
            ]
        )
