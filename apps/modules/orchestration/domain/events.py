from typing import ClassVar

from uuid import UUID

from pydantic import PositiveInt

from modules.shared_kernel.domain import Event


class AudioPrecessedEvent(Event):
    event_type: ClassVar[str] = "audio_processed"

    collection_id: UUID
    chunk_count: PositiveInt


class AudioTranscribedEvent(Event):
    event_type: ClassVar[str] = "audio_transcribed"

    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    transcription: str
