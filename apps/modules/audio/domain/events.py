from typing import ClassVar

from uuid import UUID

from modules.shared_kernel.domain import Event
from modules.shared_kernel.file_management import Filepath


class RecordAddedEvent(Event):
    """Аудио запись добавлена в коллекцию"""
    event_type: ClassVar[str] = "audio_record_added"

    collection_id: UUID
    record_id: UUID
    filepath: Filepath
