from typing import ClassVar

from uuid import UUID

from pydantic import PositiveInt

from modules.shared_kernel.domain import Event

from .value_objects import SummaryFormat, SummaryType


class SummarizationTaskCreatedEvent(Event):
    event_type: ClassVar[str] = "summarization_task_created"

    task_id: UUID
    collection_id: UUID
    summary_type: SummaryType
    summary_format: SummaryFormat


class AudioProcessedEvent(Event):
    event_type: ClassVar[str] = "audio_processed"

    collection_id: UUID
    segments_count: PositiveInt


class SoundQualityEnhancedEvent(Event):
    event_type: ClassVar[str] = "sound_quality_enhanced"

    collection_id: UUID


class AudioTranscribedEvent(Event):
    event_type: ClassVar[str] = "audio_transcribed"

    collection_id: UUID
    record_id: UUID
    segment_id: PositiveInt
    segment_duration: PositiveInt
    segments_count: PositiveInt
    text: str
