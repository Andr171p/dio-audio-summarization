from collections.abc import AsyncIterable

from modules.shared_kernel.application import EventBus, Storage

from ..domain import (
    AddAudioRecordCommand,
    AudioCollection,
    AudioCollectionStatus,
    AudioRecord,
    CreateAudioCollectionCommand,
    SummarizeAudioCollectionCommand,
    SummarizingState,
)
from .exceptions import AudioCollectionNotFoundError
from .repository import AudioCollectionRepository


class CreateAudioCollectionUseCase:
    """Создание аудио коллекции"""
    def __init__(self, repository: AudioCollectionRepository) -> None:
        self.repository = repository

    async def execute(self, command: CreateAudioCollectionCommand) -> AudioCollection:
        collection = AudioCollection.create(command)
        return await self.repository.create(collection)


class AddAudioRecordUseCase:
    """Загрузка аудио записи в коллекцию"""

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
            raise AudioCollectionNotFoundError(
                command.collection_id, details={"collection_id": command.collection_id}
            )
        record = collection.add_record(command)
        await self.storage.upload_multipart(record.generate_file_parts(stream))
        added_record = await self.repository.add_record(record)
        for event in collection.collect_events():
            await self.eventbus.publish(event)
        return added_record


class SummarizeAudioCollectionUseCase:
    def __init__(
            self, repository: AudioCollectionRepository, eventbus: EventBus
    ) -> None:
        self.repository = repository
        self.eventbus = eventbus

    async def execute(self, command: SummarizeAudioCollectionCommand) -> SummarizingState:
        collection = await self.repository.read(command.collection_id)
        if collection is None:
            raise AudioCollectionNotFoundError(
                command.collection_id, details={"collection_id": command.collection_id}
            )
        summarizing_state = collection.summarize(command)
        for event in collection.collect_events():
            await self.eventbus.publish(event)
        await self.repository.update(
            command.collection_id, {"status": AudioCollectionStatus.PROCESSING}
        )
        return summarizing_state
