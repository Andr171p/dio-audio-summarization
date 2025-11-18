from collections.abc import AsyncIterable

from modules.shared_kernel.application import MessageBus, Storage
from modules.shared_kernel.application.exceptions import NotFoundError

from ..domain import (
    AddRecordCommand,
    AudioCollection,
    AudioRecord,
    CreateCollectionCommand,
)
from .repository import CollectionRepository


class CreateCollectionUseCase:
    """Создание аудио коллекции"""
    def __init__(self, repository: CollectionRepository) -> None:
        self.repository = repository

    async def execute(self, command: CreateCollectionCommand) -> AudioCollection:
        collection = AudioCollection.create(command)
        return await self.repository.create(collection)


class UploadRecordUseCase:
    """Загрузка аудио записи в коллекцию"""

    def __init__(
            self,
            repository: CollectionRepository,
            storage: Storage,
            message_bus: MessageBus
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.message_bus = message_bus

    async def execute(
            self, stream: AsyncIterable[bytes], command: AddRecordCommand
    ) -> AudioRecord:
        collection = await self.repository.read(command.collection_id)
        if collection is None:
            raise NotFoundError(
                f"Audio collection not found by id {command.collection_id}",
                entity_name="AudioCollection",
                details={"collection_id": command.collection_id}
            )
        record = collection.add_record(command)
        await self.storage.upload_multipart(record.generate_file_parts(stream))
        added_record = await self.repository.add_record(record)
        for event in collection.collect_events():
            await self.message_bus.send(event)
        return added_record
