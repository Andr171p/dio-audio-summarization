from enum import StrEnum

from pydantic import PositiveFloat

from domains.shared_kernel.domain import FileMetadata


class AudioStatus(StrEnum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    ERROR = "error"


class AudioFileMetadata(FileMetadata):
    duration: PositiveFloat
    samplerate: PositiveFloat | None = None
