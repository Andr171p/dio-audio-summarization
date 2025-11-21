from typing import Self

from collections.abc import AsyncIterable
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import Field, NonNegativeInt, PositiveFloat, PositiveInt

from modules.shared_kernel.domain import AggregateRoot, Entity
from modules.shared_kernel.file_management import FileMetadata, FilePart, Filepath, FileType
from modules.shared_kernel.utils import current_datetime

from .commands import AddRecordCommand, CreateCollectionCommand
from .events import RecordAddedEvent

MIN_PART_SIZE = 5 * 1024 * 1024


class CollectionStatus(StrEnum):
    """Статус аудио коллекции"""
    NEW = "new"
    UPLOADED = "uploaded"
    FROZEN = "frozen"


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

    async def generate_file_parts(
            self, stream: AsyncIterable[bytes], min_part_size: PositiveInt = MIN_PART_SIZE
    ) -> AsyncIterable[FilePart]:
        """Асинхронный генератор для потоковой загрузки файла по частям

        :param stream: Байтовых поток файла, которые нужно загрузить.
        :param min_part_size: Минимальный размер части файла.
        """
        part_number = 1
        buffer = b""
        async for chunk in stream:
            buffer += chunk
            while len(buffer) >= min_part_size:
                content_part = buffer[:min_part_size]
                buffer = buffer[min_part_size:]
                yield FilePart(
                    filepath=self.filepath,
                    filesize=self.metadata.filesize,
                    content=content_part,
                    part_size=len(content_part),
                    part_number=part_number,
                )
            part_number += 1
        # Отправка оставшихся данных (последняя часть может быть меньше min_part_size)
        if buffer:
            yield FilePart(
                filepath=self.filepath,
                filesize=self.metadata.filesize,
                content=buffer,
                part_size=len(buffer),
                part_number=part_number,
            )


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
    status: CollectionStatus
    record_count: NonNegativeInt = Field(default=0)
    records: list[AudioRecord] = Field(default_factory=list)

    @property
    def total_duration(self) -> int:
        """Общая продолжительность коллекции в секундах"""
        return sum(record.metadata.duration for record in self.records)

    @classmethod
    def create(cls, command: CreateCollectionCommand) -> Self:
        """Создание коллекции"""
        return cls(
            user_id=command.user_id, topic=command.topic, status=CollectionStatus.NEW
        )

    def _set_status(self, status: CollectionStatus) -> None:
        self.status = status

    def add_record(self, command: AddRecordCommand) -> AudioRecord:
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
        self._set_status(CollectionStatus.UPLOADED)
        self._register_event(RecordAddedEvent(
            collection_id=self.id, record_id=record_id, filepath=filepath
        ))
        return record

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
