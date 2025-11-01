from domains.shared_kernel.application import EventBus

from ..domain.aggregates import AudioCollection
from ..domain.commands import AddAudioRecordCommand, CreateAudioCollectionCommand
from ..domain.exceptions import AudioCollectionNotFoundError
from .base import AudioCollectionRepository


class CreateAudioCollectionUseCase:
    """Создание аудио коллекции"""
    def __init__(self, repository: AudioCollectionRepository) -> None:
        self.repository = repository

    async def execute(self, command: CreateAudioCollectionCommand) -> AudioCollection:
        collection = AudioCollection.create(command)
        return await self.repository.create(collection)


class UploadAudioRecordUseCase:
    """Загрузка аудио в коллекцию"""
    def __init__(self, repository: AudioCollectionRepository, eventbus: EventBus) -> None:
        self.repository = repository
        self.eventbus = eventbus

    async def execute(self, command: AddAudioRecordCommand) -> None:
        collection = await self.repository.read(command.collection_id)
        if collection is None:
            raise AudioCollectionNotFoundError(f"")
        collection.add_record(command)
        await self.repository.create(collection)
        for event in collection.collect_events():
            await self.eventbus.publish(event)
