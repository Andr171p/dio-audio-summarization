from abc import ABC
from collections.abc import Iterator
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from ..utils import current_datetime
from .event import EventT


class Entity(BaseModel, ABC):
    """Базовая модель для доменной сущности"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True)


class AggregateRoot(BaseModel, ABC):
    """Корень агрегата"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)

    _events: list[EventT] = PrivateAttr(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    def _register_event(self, event: EventT) -> None:
        """Добавление нового доменного события"""
        self._events.append(event)

    def collect_events(self) -> Iterator[EventT]:
        """Собирает и возвращает все накопленные события"""
        while self._events:
            yield self._events.pop(0)
