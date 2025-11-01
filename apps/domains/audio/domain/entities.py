from typing import Self

from datetime import datetime
from uuid import UUID, uuid4

from domains.shared_kernel.domain import Entity, File, Filepath, FileType
from domains.shared_kernel.utils import current_datetime

from .commands import AddAudioRecordCommand
from .value_objects import AudioFileMetadata, AudioStatus


class AudioRecord(Entity):
    """Аудио запись"""
    collection_id: UUID
    filepath: Filepath
    status: AudioStatus
    metadata: AudioFileMetadata

    @classmethod
    def create(
            cls, user_id: UUID, command: AddAudioRecordCommand
    ) -> tuple[Self, File]:
        file_id, created_at = uuid4(), current_datetime()
        filepath = cls._build_filepath(
            user_id=user_id,
            collection_id=command.collection_id,
            file_id=file_id,
            created_at=created_at,
            format=command.filename.split(".")[-1],
        )
        record = cls(
            id=file_id,
            collection_id=command.collection_id,
            filepath=filepath,
            status=AudioStatus.UPLOADING,
            metadata=cls._create_metadata(command),
        )
        file = File(filepath=filepath, filesize=command.filesize, content=command.content)
        return record, file

    @staticmethod
    def _build_filepath(
            user_id: UUID,
            collection_id: UUID,
            file_id: UUID,
            created_at: datetime,
            format: str  # noqa: A002
    ) -> Filepath:
        return Filepath(f"audio/{user_id}/{collection_id}/{file_id}_{created_at}.{format}")

    @staticmethod
    def _create_metadata(command: AddAudioRecordCommand) -> AudioFileMetadata:
        return AudioFileMetadata(
            filename=command.filename,
            filesize=command.filesize,
            duration=command.duration,
            format=command.filename.split(".")[-1],
            type=FileType.AUDIO,
            created_at=command.created_at,
        )
