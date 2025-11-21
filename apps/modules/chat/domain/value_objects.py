from typing import NotRequired, TypedDict

from enum import StrEnum

from modules.shared_kernel.domain import StrPrimitive


class FileType(StrEnum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class Filename(StrPrimitive):
    @classmethod
    def validate(cls, filename: str) -> str: ...


class DocumentMetadata(TypedDict):
    pages_count: int


class AudioMetadata(TypedDict):
    duration: int
    samplerate: NotRequired[int]
    channels: NotRequired[int]
    bitrate: NotRequired[int]


class VideoMetadata(TypedDict):
    duration: int
    resolution: str


class Role(StrEnum):
    ASSISTANT = "assistant"
    USER = "user"
