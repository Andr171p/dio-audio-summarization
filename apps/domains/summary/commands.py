from uuid import UUID

from pydantic import BaseModel


class SummarizeAudioCollectionCommand(BaseModel):
    """Суммаризовать аудио коллекцию"""
    collection_id: UUID
    summary_type: ...
