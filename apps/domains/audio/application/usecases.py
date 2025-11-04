from collections.abc import AsyncIterable

from domains.shared_kernel import EventBus, Storage

from ..domain.aggregates import AudioCollection
from ..domain.commands import AddAudioRecordCommand, CreateAudioCollectionCommand
from ..domain.entities import AudioRecord
from ..domain.exceptions import AudioCollectionNotFoundError
from .base import AudioCollectionRepository


class CreateAudioCollectionUseCase:
    """Создание аудио коллекции"""
    def __init__(self, repository: AudioCollectionRepository) -> None:
        self.repository = repository

    async def execute(self, command: CreateAudioCollectionCommand) -> AudioCollection:
        collection = AudioCollection.create(command)
        return await self.repository.create(collection)


class AddAudioRecordUseCase:
    """Загрузка аудио в коллекцию"""
    def __init__(
            self,
            repository: AudioCollectionRepository,
            storage: Storage,
            eventbus: EventBus
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.eventbus = eventbus

    async def execute(
            self, stream: AsyncIterable[bytes], command: AddAudioRecordCommand
    ) -> AudioRecord:
        collection = await self.repository.read(command.collection_id)
        if collection is None:
            raise AudioCollectionNotFoundError("")
        record = collection.add_record(command)
        file_parts = record.streaming_upload(stream)
        await self.storage.upload_multipart(file_parts)
        added_record = await self.repository.add_record(record)
        for event in collection.collect_events():
            await self.eventbus.publish(event)
        return added_record
