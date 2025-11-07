from uuid import UUID

from pydantic import BaseModel


class SplitAudioCommand(BaseModel):
    collection_id: UUID


class ConvertAudioCommand(BaseModel):
    ...


class EnhanceSoundQualityCommand(BaseModel):
    ...


class TranscribeAudioCommand(BaseModel):
    ...


class SummarizeTranscriptionCommand(BaseModel):
    ...
