from uuid import UUID

from pydantic import PositiveInt

from modules.shared_kernel.domain import Command


class ProcessAudioCommand(Command):
    """Команда для инициации процесса обработки аудио.

    Attributes:
        collection_id: Коллекция, которую нудно обработать.
    """
    collection_id: UUID


class EnhanceSoundQualityCommand(Command):
    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    chunk_content: bytes
    chunk_format: str


class TranscribeAudioCommand(Command):
    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    chunk_content: bytes
    samplerate: PositiveInt


class SummarizeTranscriptionCommand(Command):
    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    transcription_id: UUID
    summary_type: str
    document_format: str
