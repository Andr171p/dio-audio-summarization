from uuid import UUID

from modules.shared_kernel.domain import Command

from .entities import SummaryFormat, SummaryType


class CreateSummarizationTaskCommand(Command):
    """Инициация суммаризации аудио"""
    collection_id: UUID
    summary_type: SummaryType
    summary_format: SummaryFormat


class ProcessAudioCommand(Command):
    ...
