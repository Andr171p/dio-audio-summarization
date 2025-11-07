from collections.abc import AsyncIterable

from modules.shared_kernel.application import EventBus, Storage
from modules.shared_kernel.file_managment import FilePart

from ..domain import (
    AddRecordCommand,
    AudioCollection,
    AudioRecord,
    CreateCollectionCommand,
    DownloadRecordQuery,
)
from .exceptions import AudioCollectionNotFoundError
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
            eventbus: EventBus
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.eventbus = eventbus

    async def execute(
            self, stream: AsyncIterable[bytes], command: AddRecordCommand
    ) -> AudioRecord:
        collection = await self.repository.read(command.collection_id)
        if collection is None:
            raise AudioCollectionNotFoundError(
                command.collection_id, details={"collection_id": command.collection_id}
            )
        record = collection.add_record(command)
        await self.storage.upload_multipart(record.generate_file_parts(stream))
        added_record = await self.repository.add_record(record)
        for event in collection.collect_events():
            await self.eventbus.publish(event)
        return added_record


class DownloadRecordUseCase:
    def __init__(self, repository: CollectionRepository, storage: Storage) -> None:
        self.repository = repository
        self.storage = storage

    async def execute(self, query: DownloadRecordQuery) -> AsyncIterable[FilePart]:
        record = await self.repository.get_record(query.collection_id, query.record_id)
        async for file_part in await self.storage.download_multipart(
                record.filepath, part_size=query.chunk_size
        ):
            yield file_part
