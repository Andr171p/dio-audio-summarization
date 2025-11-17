from modules.shared_kernel.application import Storage

from ..domain import (
    AudioSplitEvent,
    AudioTranscribedEvent,
    SoundEnhancedEvent,
    SummarizeTranscriptionCommand,
    TaskStatus,
    Transcription,
    TranscriptionSummarizedEvent,
)
from ..utils import compile_document
from .repositories import SummaryRepository, TaskRepository, TranscriptionRepository


class AudioSplitEventHandler:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    async def handle(self, event: AudioSplitEvent) -> ...:
        return await self.task_repository.update(event.task_id, status=TaskStatus.SPLIT)


class SoundEnhancedEventHandler:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    async def handle(self, event: SoundEnhancedEvent) -> ...:
        return await self.task_repository.update(event.task_id, status=TaskStatus.SOUND_ENHANCED)


class AudioTranscribedEventHandler:
    def __init__(
            self,
            task_repository: TaskRepository,
            transcription_repository: TranscriptionRepository
    ) -> None:
        self.task_repository = task_repository
        self.transcription_repository = transcription_repository

    async def handle(self, event: AudioTranscribedEvent) -> SummarizeTranscriptionCommand | None:
        transcription = Transcription.from_event(event)
        await self.transcription_repository.create(transcription)
        if not event.is_last:
            return None
        updated_task = await self.task_repository.update(
            event.task_id, status=TaskStatus.TRANSCRIBED
        )
        return SummarizeTranscriptionCommand(collection_id=updated_task.collection_id)


class TranscriptionSummarizedEventHandler:
    def __init__(
            self,
            task_repository: TaskRepository,
            summary_repository: SummaryRepository,
            storage: Storage,
    ) -> None:
        self.task_repository = task_repository
        self.summary_repository = summary_repository
        self.storage = storage

    async def handle(self, event: TranscriptionSummarizedEvent) -> ...:
        task = await self.task_repository.read(event.task_id)
        document = compile_document(
            title=event.summary_title, text=event.summary_text, format=task.document_format
        )
        summary, file = task.prepare_summary_for_upload(event, document)
        await self.storage.upload(file)
        await self.summary_repository.create(summary)
        await self.task_repository.update(event.task_id, status=TaskStatus.SUMMARIZED)
