from uuid import UUID

from pydantic import BaseModel, PositiveFloat

from .entities import AudioChunk


class ProcessAudioCommand(BaseModel):
    collection_id: UUID
    output_format: str
    chunk_duration: PositiveFloat


class EnhanceSoundQualityCommand(BaseModel):
    audio_chunk: AudioChunk


class TranscribeAudioCommand(BaseModel):
    ...


class SummarizeTranscriptionCommand(BaseModel):
    ...
