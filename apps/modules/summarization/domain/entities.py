from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import PositiveFloat, PositiveInt

from modules.shared_kernel.domain import Entity
from modules.shared_kernel.file_managment import FileMetadata, Filepath


class SummaryType(StrEnum):
    """Типы суммаризации"""
    MEETING_PROTOCOL = "meeting_protocol"  # Протокол совещания
    LECTURE_NOTES = "lecture_notes"  # Конспект лекции


class SummaryFormat(StrEnum):
    """Формат документа саммари"""
    DOCX = "docx"
    PDF = "pdf"
    MD = "md"


class TaskStatus(StrEnum):
    """Статус задачи"""
    PENDING = "pending"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


class SummarizationTask(Entity):
    """Задача на суммаризацию"""
    status: TaskStatus
    waiting_time: PositiveFloat
    updated_at: datetime


class DocumentFileMetadata(FileMetadata):
    """Мета-данные файлового документа"""
    page_count: PositiveInt


class Summary(Entity):
    """Суммаризация аудио

    Attributes:
        collection_id: Аудио-коллекция к которой принадлежит суммаризация
        type: Тип саммари, например протокол совещания или конспект лекции
        title: Заголовок/название самари
        md_text: Текст в формате Markdown
        filepath: Путь до файла в хранилище (файл в формате pdf, docx, txt, ...)
        metadata: Мета-данные файла
    """
    collection_id: UUID
    type: SummaryType
    title: str
    md_text: str
    filepath: Filepath
    metadata: DocumentFileMetadata
