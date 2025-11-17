from uuid import UUID

from modules.shared_kernel.domain import Command

from .entities import DocumentFormat, SummaryType


class CreateSummarizationTaskCommand(Command):
    """Инициация суммаризации аудио"""
    collection_id: UUID
    summary_type: SummaryType
    document_format: DocumentFormat
    template_id: UUID | None = None


class SummarizeTranscriptionCommand(Command):
    """Команда для начала суммаризации транскрибации аудио коллекции"""
    collection_id: UUID
