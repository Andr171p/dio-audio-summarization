from uuid import UUID

from pydantic import BaseModel

from .entities import SummaryFormat, SummaryType


class CreateSummarizationTaskCommand(BaseModel):
    """Инициация суммаризации аудио"""
    collection_id: UUID
    summary_type: SummaryType
    summary_format: SummaryFormat
