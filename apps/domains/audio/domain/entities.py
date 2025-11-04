from typing import Self

from collections.abc import AsyncIterable
from datetime import datetime
from uuid import UUID, uuid4

from domains.shared_kernel import Entity, Filepath, FileType
from domains.shared_kernel.file_managment import FilePart
from domains.shared_kernel.utils import current_datetime

from .commands import AddAudioRecordCommand
from .value_objects import AudioFileMetadata, AudioStatus


class AudioRecord(Entity):
    """Аудио запись"""
    collection_id: UUID
    filepath: Filepath
    status: AudioStatus
    metadata: AudioFileMetadata

    async def streaming_upload(self, stream: AsyncIterable[bytes]) -> AsyncIterable[FilePart]:
        part_number = 1
        async for chunk in stream:
            if not chunk:
                ...
            yield FilePart(
                filepath=self.filepath,
                filesize=self.metadata.filesize,
                content=chunk,
                part_number=part_number,
            )
            part_number += 1

    @classmethod
    def create(
            cls, command: AddAudioRecordCommand
    ) -> Self:
        record_id, created_at = uuid4(), current_datetime()
        filepath = cls._build_filepath(
            user_id=command.user_id,
            collection_id=command.collection_id,
            record_id=record_id,
            created_at=created_at,
            format=command.filename.split(".")[-1],
        )
        return cls(
            id=record_id,
            collection_id=command.collection_id,
            filepath=filepath,
            status=AudioStatus.UPLOADING,
            metadata=cls._create_metadata(command),
            created_at=created_at,
        )

    @staticmethod
    def _build_filepath(
            user_id: UUID,
            collection_id: UUID,
            record_id: UUID,
            created_at: datetime,
            format: str  # noqa: A002
    ) -> Filepath:
        return Filepath(f"audio/{user_id}/{collection_id}/{record_id}_{created_at}.{format}")

    @staticmethod
    def _create_metadata(command: AddAudioRecordCommand) -> AudioFileMetadata:
        return AudioFileMetadata(
            filename=command.filename,
            filesize=command.filesize,
            duration=command.duration,
            samplerate=command.samplerate,
            channels=command.channels,
            format=command.filename.split(".")[-1],
            type=FileType.AUDIO,
            created_at=command.created_at,
        )
