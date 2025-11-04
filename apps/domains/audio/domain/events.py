from typing import ClassVar

from domains.shared_kernel import Event, File, Filepath

from .entities import AudioRecord


class AudioRecordAddedEvent(Event):
    """Добавление аудио-записи"""
    record: AudioRecord
    file: File


class UploadingCreatedEvent(Event):
    event_type: ClassVar[str] = "uploading_created"

    filepath: Filepath


class UploadingCompletedEvent(Event):
    ...


class FileUploadedEvent(Event):
    event_type: ClassVar[str] = "file_uploaded"

    upload_id: str
    filepath: Filepath
    chunk: bytes
    chunk_number: int


class UploadingAbortedEvent(Event):
    ...


class AudioRecordUploadedEvent(Event):
    filepath: ...
    part_number: ...
