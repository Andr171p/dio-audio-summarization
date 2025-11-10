from uuid import UUID

from pydantic import PositiveFloat, PositiveInt

from modules.shared_kernel.domain import Command


class ProcessAudioCommand(Command):
    """Команда для инициации процесса обработки аудио.

    Attributes:
        collection_id: Коллекция, которую нудно обработать.
        output_format: Формат аудио к которому нужно привести все аудио записи.
        chunk_duration: Продолжительность чанка в секундах (для разбиения аудио записей на чанки)
    """
    collection_id: UUID
    output_format: str
    chunk_duration: PositiveFloat


class EnhanceSoundQualityCommand(Command):
    collection_id: UUID
    record_id: UUID
    chunk_number: PositiveInt
    chunk_content: bytes
    output_format: str


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
