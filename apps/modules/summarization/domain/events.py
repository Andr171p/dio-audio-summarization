from typing import ClassVar

from uuid import UUID

from pydantic import PositiveInt

from modules.shared_kernel.domain import Event

from .value_objects import DocumentFormat, SummaryType, TaskStatus


class SummarizationTaskCreatedEvent(Event):
    event_type: ClassVar[str] = "summarization_task_created"

    task_id: UUID
    collection_id: UUID
    summary_type: SummaryType
    document_format: DocumentFormat


class TaskStatusChangedEvent(Event):
    event_type: ClassVar[str] = "task_status_changed"

    task_id: UUID
    collection_id: UUID
    new_status: TaskStatus


class AudioSplitEvent(Event):
    event_type: ClassVar[str] = "audio_split"

    task_id: UUID
    collection_id: UUID
    segments_count: PositiveInt


class SoundEnhancedEvent(Event):
    event_type: ClassVar[str] = "sound_enhanced"

    task_id: UUID
    collection_id: UUID
    segment_id: PositiveInt
    segments_count: PositiveInt
    is_last: bool


class AudioTranscribedEvent(Event):
    event_type: ClassVar[str] = "audio_transcribed"

    task_id: UUID
    collection_id: UUID
    record_id: UUID
    segment_id: PositiveInt
    segment_duration: PositiveInt
    segments_count: PositiveInt
    is_last: bool
    text: str


class TranscriptionSummarizedEvent(Event):
    event_type: ClassVar[str] = "transcription_summarized"

    task_id: UUID
    collection_id: UUID
    summary_type: SummaryType
    summary_title: str
    summary_text: str
