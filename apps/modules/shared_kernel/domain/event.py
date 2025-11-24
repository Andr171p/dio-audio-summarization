from typing import ClassVar, TypeVar

from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..utils import current_datetime, generate_correlation_id


class Event(BaseModel, ABC):
    """Базовая модель доменного события.

    Attributes:
        correlation_id: Уникальный идентификатор события (для трассировки)
        event_id: Уникальный идентификатор события
        event_version: Версия события
        event_type: Тип события, например: 'audio_uploaded', 'user_registered', ...
        (Может использоваться как название очереди для брокера сообщений)
        occurred_on: Дата и время генерации ивента.
    """

    correlation_id: str = Field(default_factory=generate_correlation_id)
    event_id: UUID = Field(default_factory=uuid4)
    event_version: int = Field(default=1)
    event_type: ClassVar[str]
    occurred_on: datetime = Field(default_factory=current_datetime)


EventT = TypeVar("EventT", bound=Event)
