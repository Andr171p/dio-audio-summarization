from collections.abc import Iterator
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .events import EventT
from .utils import current_datetime


class Entity(BaseModel):
    """Базовая модель для доменной сущности"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)


class AggregateRoot(BaseModel):
    """Корень агрегата"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)

    __events: list[EventT] = Field(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    def _register_event(self, event: EventT) -> None:
        """Добавление нового доменного события"""
        self.__events.append(event)

    def collect_events(self) -> Iterator[EventT]:
        """Собирает и возвращает все накопленные события"""
        while self.__events:
            yield self.__events.pop(0)
