from typing import Literal

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Metadata(BaseModel):
    """Мета-информация аудио записи"""
    filename: str
    filesize: float
    format: str
    type: str
    uploaded_at: datetime
    duration: float
    channels: int | None = None
    samplerate: float | None = None
    bitrate: int | None = None


class Record(BaseModel):
    """Аудио запись"""
    id: UUID
    collection_id: UUID
    filepath: str
    metadata: Metadata


class Collection(BaseModel):
    """Аудио коллекция, основой агрегат аудио записей"""
    id: UUID
    user_id: UUID
    topic: str
    status: Literal["new", "uploaded", "frozen"]
    record_count: int
    records: list[Record]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)

    @property
    def total_duration(self) -> int:
        return sum(record.metadata.duration for record in self.records)
