from typing import Self

from datetime import datetime
from uuid import UUID

from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import AggregateRoot, Entity
from modules.shared_kernel.file_managment import Filepath
from modules.shared_kernel.utils import current_datetime

from .events import SummarizationTaskCreatedEvent
from .value_objects import DocumentFileMetadata, SummaryFormat, SummaryType, TaskStatus


class SummarizationTask(AggregateRoot):
    """Задача на суммаризацию.

    Attributes:
        collection_id: Коллекция для которой выполняется суммаризация.
        summary_type: Тип суммаризации.
        summary_format: Выходной формат документа с суммаризацией.
        status: Статус суммаризации.
        waiting_time: Примерное оставшееся время ожидания (обновляется после смены статуса).
        updated_at: Время обновления задачи.
    """
    collection_id: UUID
    summary_type: SummaryType
    summary_format: SummaryFormat
    status: TaskStatus
    waiting_time: PositiveInt
    updated_at: datetime = Field(default_factory=current_datetime)

    @classmethod
    def create(
            cls,
            collection_id: UUID,
            total_duration: int,
            summary_type: SummaryType,
            summary_format: SummaryFormat
    ) -> Self:
        task = cls(
            collection_id=collection_id,
            summary_type=summary_type,
            summary_format=summary_format,
            status=TaskStatus.PENDING,
            waiting_time=total_duration // 5,  # Сделать нормальный расчёт приблизительного времени
        )
        cls._register_event(task, SummarizationTaskCreatedEvent(
            task_id=task.id,
            collection_id=collection_id,
            summary_type=summary_type,
            summary_format=summary_format
        ))
        return task

    def update_status(self, new_status: TaskStatus) -> None:
        self.status = new_status


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
