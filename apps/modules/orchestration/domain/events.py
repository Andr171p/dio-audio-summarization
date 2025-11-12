from typing import ClassVar

from uuid import UUID

from pydantic import PositiveFloat, PositiveInt

from modules.shared_kernel.domain import Event


class AudioProcessingStatedEvent(Event):
    event_type: ClassVar[str] = "audio_processing_stated"

    chunk_count: PositiveInt


class ChunkPrecessedEvent(Event):
    event_type: ClassVar[str] = "chunk_processed"

    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    chunks_count: PositiveInt
    chunk_format: str
    chunk_content: bytes
    chunk_size: PositiveFloat
    chunk_duration: PositiveFloat


class SoundQualityEnhancedEvent(Event):
    event_type: ClassVar[str] = "sound_quality_enhanced"

    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    chunk_content: bytes
    audio_format: str
    samplerate: PositiveFloat


class AudioTranscribedEvent(Event):
    event_type: ClassVar[str] = "audio_transcribed"

    collection_id: UUID
    record_id: UUID
    transcription: dict[str, str]


class TranscriptionSummarizedEvent(Event):
    event_type: ClassVar[str] = "transcription_summarized"
