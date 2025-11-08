from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Metadata(BaseModel):
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
    id: UUID
    collection_id: UUID
    filepath: str
    metadata: Metadata


class Collection(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    status: str
    record_count: int
    records: list[Record]
    created_at: datetime
