from uuid import UUID

from pydantic import BaseModel, PositiveFloat


class SplitAudioRecordsCommand(BaseModel):
    """Разбиение аудио записей на чанки (для повышения производительности)"""
    collection_id: UUID
    record_presigned_urls: list[str]
    collection_duration: PositiveFloat
    segment_duration: PositiveFloat
