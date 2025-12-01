from typing import NotRequired, TypedDict

from enum import StrEnum


class FileType(StrEnum):

    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


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


class MessageRole(StrEnum):

    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
