from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, PositiveFloat

from domains.shared_kernel.utils import current_datetime


class AddAudioRecordCommand(BaseModel):
    collection_id: UUID
    filename: str
    filesize: PositiveFloat
    duration: PositiveFloat
    samplerate: PositiveFloat
    content: bytes
    created_at: datetime = Field(default_factory=current_datetime)


class CreateAudioCollectionCommand(BaseModel):
    """Загрузка коллекции аудио-файлов"""
    user_id: UUID
    topic: str = Field(default="")
