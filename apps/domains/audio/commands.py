from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from domains.shared_kernel import current_datetime


class CreateAudioCollectionCommand(BaseModel):
    """Загрузка коллекции аудио-файлов"""
    user_id: UUID
    topic: str = Field(default="")


class AddAudioRecordCommand(BaseModel):
    """Добавление аудио записи в коллекцию"""
    user_id: UUID
    collection_id: UUID
    filename: str
    filesize: PositiveFloat
    duration: PositiveFloat
    samplerate: PositiveFloat | None = None
    channels: PositiveInt | None = None
    bitrate: PositiveInt | None = None
    created_at: datetime = Field(default_factory=current_datetime)


class SummarizeAudioCollectionCommand(BaseModel):
    """Суммаризовать аудио коллекцию"""
    collection_id: UUID
    summary_type: str
