from enum import StrEnum

from pydantic import PositiveInt

from modules.shared_kernel.file_managment import FileMetadata


class DocumentFileMetadata(FileMetadata):
    """Мета-данные документа"""
    page_count: PositiveInt


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
