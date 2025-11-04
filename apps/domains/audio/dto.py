from uuid import UUID

from pydantic import BaseModel, PositiveInt

from .domain import AudioCollectionStatus


class SummarizingState(BaseModel):
    collection_id: UUID
    records_summarizing: list[UUID]
    status: AudioCollectionStatus
    approximate_waiting_time: PositiveInt


class AudioCollectionSummarize(BaseModel):
    summary_type: ...
