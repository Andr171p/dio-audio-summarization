from typing import Self

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field, PositiveInt, model_validator

from modules.shared_kernel.domain import AggregateRoot, Entity
from modules.shared_kernel.file_managment import File, Filepath
from modules.shared_kernel.utils import current_datetime

from .events import (
    AudioTranscribedEvent,
    SummarizationTaskCreatedEvent,
    TranscriptionSummarizedEvent,
)
from .value_objects import Document, DocumentFileMetadata, DocumentFormat, SummaryType, TaskStatus


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


class SummarizationTask(AggregateRoot):
    """Задача на суммаризацию.

    Attributes:
        collection_id: Коллекция для которой выполняется суммаризация.
        summary_type: Тип суммаризации.
        document_format: Выходной формат документа с суммаризацией.
        status: Статус суммаризации.
        waiting_time: Примерное оставшееся время ожидания (обновляется после смены статуса).
        summary_id: Идентификатор готовой суммаризации (не nullable при статусе 'completed')
        updated_at: Время обновления задачи.
    """
    collection_id: UUID
    summary_type: SummaryType
    document_format: DocumentFormat
    status: TaskStatus
    waiting_time: PositiveInt
    summary_id: UUID | None = None
    updated_at: datetime = Field(default_factory=current_datetime)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Проверка состояния инварианта"""
        if self.status == TaskStatus.COMPLETED and self.summary_id is None:
            raise ValueError("Completed task must have summary id")
        return self

    @classmethod
    def create(
            cls,
            collection_id: UUID,
            total_duration: int,
            summary_type: SummaryType,
            document_format: DocumentFormat,
    ) -> Self:
        """Создание задачи на суммаризацию.

        :param collection_id: Идентификатор коллекции.
        :param total_duration: Полная длительность всей коллекции.
        :param summary_type: Тип саммари.
        :param document_format: Формат документа для саммари, например: 'pdf', 'docx', ...
        :returns: Созданная задача на суммаризацию.
        """
        task = cls(
            collection_id=collection_id,
            summary_type=summary_type,
            document_format=document_format,
            status=TaskStatus.PENDING,
            waiting_time=total_duration // 5,  # Сделать нормальный расчёт приблизительного времени
        )
        cls._register_event(task, SummarizationTaskCreatedEvent(
            task_id=task.id,
            collection_id=collection_id,
            summary_type=summary_type,
            document_format=document_format,
        ))
        return task

    def _build_document_filepath(self, summary_id: UUID, created_at: datetime) -> Filepath:
        """Построение системного пути до файла с суммаризацией.

        :param summary_id: Идентификатор саммари.
        :param created_at: Дата и время создания саммари.
        :returns: Системный путь до файла в хранилище.
        """
        return Filepath(
            f"documents/{self.collection_id}/{summary_id}_{created_at}.{self.document_format.value}"
        )

    def prepare_summary_for_upload(
            self, event: TranscriptionSummarizedEvent, document: Document
    ) -> tuple[Summary, File]:
        """Подготовка саммари к загрузке в хранилище:
         - Составление системного пути для хранилища
         - Получение мета-данных
         - Формирование сущностей

        :param event: Событие успешно суммаризованной трансрибации.
        :param document: Составленный саммари-документ.
        :returns: Метаданные саммари + файл для загрузки в хранилище.
        """
        summary_id, created_at = uuid4(), current_datetime()
        filepath = self._build_document_filepath(summary_id, created_at)
        summary = Summary(
            id=summary_id,
            collection_id=self.collection_id,
            type=self.summary_type,
            title=event.summary_title,
            text=event.summary_text,
            filepath=filepath,
            metadata=DocumentFileMetadata(
                filename=document.filename,
                filesize=document.size,
                format=document.format,
                pages_count=document.pages_count,
            ),
            created_at=created_at,
        )
        self.summary_id = self.summary_id
        file = File(filepath=filepath, filesize=document.size, content=document.content)
        return summary, file


class Transcription(Entity):
    """Транскрибация аудио сегмента"""

    record_id: UUID
    segment_id: PositiveInt
    segment_duration: PositiveInt
    text: str

    @classmethod
    def from_event(cls, event: AudioTranscribedEvent) -> Self:
        return cls(
            record_id=event.record_id,
            segment_id=event.segment_id,
            segment_duration=event.segment_duration,
            text=event.text,
        )


class SummaryTemplate(Entity):
    """Шаблон для суммаризации"""

    user_id: UUID
    filepath: Filepath
    text: str
