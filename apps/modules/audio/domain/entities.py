from typing import Self

from collections.abc import AsyncIterable
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeInt, PositiveFloat, PositiveInt

from modules.shared_kernel.domain import AggregateRoot, Entity
from modules.shared_kernel.file_managment import FileMetadata, FilePart, Filepath, FileType
from modules.shared_kernel.utils import current_datetime

from .commands import (
    AddAudioRecordCommand,
    CreateAudioCollectionCommand,
    SummarizeAudioCollectionCommand,
)
from .events import AudioCollectionSummarizationStartedEvent, AudioRecordAddedEvent


class AudioCollectionStatus(StrEnum):
    """Статус аудио коллекции"""
    NEW = "new"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    CONVERTED = "converted"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    ERROR = "error"


class SummarizingState(BaseModel):
    collection_id: UUID
    records_summarizing: list[UUID]
    status: AudioCollectionStatus
    approximate_waiting_time: PositiveInt


class AudioFileMetadata(FileMetadata):
    duration: PositiveFloat
    channels: PositiveInt | None = None
    samplerate: PositiveFloat | None = None
    bitrate: PositiveInt | None = None


class AudioRecord(Entity):
    """Аудио запись"""
    collection_id: UUID
    filepath: Filepath
    metadata: AudioFileMetadata

    async def generate_file_parts(self, stream: AsyncIterable[bytes]) -> AsyncIterable[FilePart]:
        """Асинхронный генератор для потоковой загрузки файла по частям"""
        part_number = 1
        async for chunk in stream:
            yield FilePart(
                filepath=self.filepath,
                filesize=self.metadata.filesize,
                content=chunk,
                part_number=part_number,
            )
            part_number += 1


class AudioCollection(AggregateRoot):
    """Коллекция с аудио-записями пользователя. Агрегирует и предоставляет доступ
    к аудио контенту.
    Загрузка аудио должна происходить только через агрегат (существование AudioRecord
    без AudioCollection не допустимо)

    Attributes:
        user_id: Пользователь, которому принадлежит коллекция.
        topic: Тема/название коллекции, по умолчанию пустая либо 'Untitled'.
        records: Загруженные аудио-записи.
    """
    user_id: UUID
    topic: str
    status: AudioCollectionStatus
    record_count: NonNegativeInt = Field(default=0)
    records: list[AudioRecord] = Field(default_factory=list)

    def _set_status(self, new_status: AudioCollectionStatus) -> None:
        """Установка нового статуса"""
        self.status = new_status

    @classmethod
    def create(cls, command: CreateAudioCollectionCommand) -> Self:
        """Создание коллекции"""
        return cls(
            user_id=command.user_id, topic=command.topic, status=AudioCollectionStatus.NEW
        )

    def add_record(self, command: AddAudioRecordCommand) -> AudioRecord:
        """Добавление аудио записи в коллекцию"""
        record_id, created_at = uuid4(), current_datetime()
        filepath = self._build_record_filepath(
            user_id=command.user_id,
            collection_id=command.collection_id,
            record_id=record_id,
            created_at=created_at,
            format=command.filename.split(".")[-1],
        )
        record = AudioRecord(
            id=record_id,
            collection_id=command.collection_id,
            filepath=filepath,
            metadata=AudioFileMetadata(
                filename=command.filename,
                filesize=command.filesize,
                duration=command.duration,
                samplerate=command.samplerate,
                channels=command.channels,
                format=command.filename.split(".")[-1],
                type=FileType.AUDIO,
                created_at=command.created_at,
            ),
            created_at=created_at,
        )
        self.records.append(record)
        self.record_count += 1
        self._set_status(AudioCollectionStatus.UPLOADED)
        self._register_event(AudioRecordAddedEvent(
            collection_id=self.id, record_id=record_id, filepath=filepath
        ))
        return record

    def summarize(self, command: SummarizeAudioCollectionCommand) -> SummarizingState:
        waiting_time = self._calculate_approximate_summarization_time()
        self._register_event(AudioCollectionSummarizationStartedEvent(
            collection_id=self.id,
            record_files=[record.filepath for record in self.records],
            summary_type=command.summary_type
        ))
        self._set_status(AudioCollectionStatus.PROCESSING)
        return SummarizingState(
            collection_id=self.id,
            records_summarizing=[record.id for record in self.records],
            status=self.status,
            approximate_waiting_time=waiting_time,
        )

    @staticmethod
    def _build_record_filepath(
            user_id: UUID,
            collection_id: UUID,
            record_id: UUID,
            created_at: datetime,
            format: str  # noqa: A002
    ) -> Filepath:
        """Создание системного пути до файла с аудио записью"""
        return Filepath(f"audio/{user_id}/{collection_id}/{record_id}_{created_at}.{format}")

    def calculate_approximate_summarization_time(self) -> int:
        """Вычисление приблизительного времени суммаризации"""
        return sum(record.metadata.duration for record in self.records) // 5
