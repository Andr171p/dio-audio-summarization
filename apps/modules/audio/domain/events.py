from typing import ClassVar

from uuid import UUID

from pydantic import PositiveFloat

from modules.shared_kernel.domain import Event
from modules.shared_kernel.file_managment import Filepath


class AudioRecordAddedEvent(Event):
    """Аудио запись добавлена в коллекцию"""
    event_type: ClassVar[str] = "audio_record_added"

    collection_id: UUID
    record_id: UUID
    filepath: Filepath


class AudioCollectionSummarizationStartedEvent(Event):
    """Инициирует операцию на суммаризацию аудио """
    event_type: ClassVar[str] = "audio_collection_summarization_started"

    collection_id: UUID
    collection_duration: PositiveFloat
    record_filepaths: list[Filepath]
    summary_type: str
    summary_format: str
