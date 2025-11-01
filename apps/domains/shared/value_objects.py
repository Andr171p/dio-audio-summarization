from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat

from .primitives import Filepath
from .utils import current_datetime


class File(BaseModel):
    filepath: Filepath
    filesize: PositiveFloat
    content: bytes
    last_modified: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True, frozen=True)


class FileType(StrEnum):
    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"


class FileMetadata(BaseModel):
    filename: str
    filesize: PositiveFloat
    format: str
    type: FileType
    created_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True)
