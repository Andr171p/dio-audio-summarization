from typing import Self

from uuid import UUID

from pydantic import Field, NonNegativeInt

from domains.shared_kernel.domain import AggregateRoot

from .commands import AddAudioRecordCommand, CreateAudioCollectionCommand
from .entities import AudioRecord
from .events import AudioRecordAddedEvent


class AudioCollection(AggregateRoot):
    """Коллекция с аудио-записями пользователя. Агрегирует и предоставляет доступ
    к аудио контенту.
    Загрузка аудио должна происходить только через агрегат (существование AudioRecord
    без AudioCollection не допустимо)

    Attributes:
        user_id: Пользователь, которому принадлежит коллекция.
        topic: Тема/название коллекции, по умолчанию пустая либо 'Untitled'.
        records: Загруженные аудио-записи.
    """
    user_id: UUID
    topic: str
    record_count: NonNegativeInt
    records: list[AudioRecord] = Field(default_factory=list)

    @classmethod
    def create(cls, command: CreateAudioCollectionCommand) -> Self:
        return cls(user_id=command.user_id, topic=command.topic)

    def add_record(self, command: AddAudioRecordCommand) -> Self:
        record, file = AudioRecord.create(self.user_id, command)
        self.records.append(record)
        self._register_event(AudioRecordAddedEvent(record=record, file=file))
        return self
