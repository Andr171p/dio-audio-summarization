from typing import ClassVar, TypeVar

from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..utils import current_datetime


class Event(BaseModel, ABC):
    """Базовая модель доменного события.

    Пример использования:

    >>> from typing import ClassVar
    >>>
    >>> from modules.shared_kernel.domain import Event
    >>>
    >>>
    >>> class MyEvent(Event):
    >>>    event_type: ClassVar[str] = "my_event"
    >>>
    >>>    foo: int
    >>>    bar: float

    Attributes:
        event_id: Уникальный идентификатор события
        event_version: Версия события
        event_type: Тип события, например: 'audio_uploaded', 'user_registered', ...
        (Может использоваться как название очереди для брокера сообщений)
        occurred_on: Дата и время генерации ивента.
    """
    event_id: UUID = Field(default_factory=uuid4)
    event_version: int = Field(default=1)
    event_type: ClassVar[str]
    occurred_on: datetime = Field(default_factory=current_datetime)


EventT = TypeVar("EventT", bound=Event)
