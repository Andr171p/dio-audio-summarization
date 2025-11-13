from typing import ClassVar

from uuid import UUID

from modules.shared_kernel.domain import Event

from .entities import SummaryFormat, SummaryType


class SummarizationTaskCreatedEvent(Event):
    event_type: ClassVar[str] = "summarization_task_created"

    task_id: UUID
    collection_id: UUID
    summary_type: SummaryType
    summary_format: SummaryFormat


class ChunkSplitEvent(Event):
    event_type: ClassVar[str] = "chunk_split"

    collection_id: UUID
    record_id: UUID


class AudioProcessedEvent(Event):
    event_type: ClassVar[str] = "audio_processed"
