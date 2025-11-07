from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from modules.shared_kernel.domain import Entity
from modules.shared_kernel.file_managment import FileMetadata, Filepath


class SpeechSegment(BaseModel):
    """Распознанная часть речи"""
    text: str
    speaker: str | None = None
    emotion: str | None = None


class Transcription(BaseModel):
    record_id: UUID
    segments: list[SpeechSegment]


class SummaryType(StrEnum):
    """Типы суммаризации"""
    MEETING_PROTOCOL = "meeting_protocol"  # Протокол совещания
    LECTURE_NOTES = "lecture_notes"  # Конспект лекции


class DocumentFileMetadata(FileMetadata):
    page_count: PositiveInt


class Summary(Entity):
    """Суммаризация аудио

    Attributes:
        collection_id: Аудио-коллекция к которой принадлежит суммаризация
        type: Тип саммари, например протокол совещания или конспект лекции
        title: Заголовок/название самари
        text: Текст в формате Markdown
        filepath: Путь до файла в хранилище (файл в формате pdf, docx, txt, ...)
        metadata: Мета-данные файла
    """
    collection_id: UUID
    type: SummaryType
    title: str
    text: str
    filepath: Filepath
    metadata: DocumentFileMetadata
