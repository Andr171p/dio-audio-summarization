from enum import StrEnum

from pydantic import PositiveInt

from modules.shared_kernel.domain import ValueObject
from modules.shared_kernel.files import FileMetadata, FileType


class TaskStatus(StrEnum):
    """Статус задачи"""
    PENDING = "pending"
    SPLIT = "split"
    SOUND_ENHANCED = "sound_enhanced"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentFileMetadata(FileMetadata):
    """Мета-данные документа"""
    type: FileType = FileType.DOCUMENT
    pages_count: PositiveInt


class DocumentFormat(StrEnum):
    """Формат документа саммари"""
    DOCX = "docx"
    PDF = "pdf"
    MD = "md"


class Document(ValueObject):
    format: DocumentFormat
    pages_count: PositiveInt
    title: str
    content: bytes
    size: PositiveInt

    @property
    def filename(self) -> str:
        return f"{self.title}.{self.format.value}"


class SummaryType(StrEnum):
    """Типы суммаризации"""
    MEETING_PROTOCOL = "meeting_protocol"  # Протокол совещания
    LECTURE_NOTES = "lecture_notes"  # Конспект лекции
