from typing import Any, ClassVar, Self, TypeVar

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from pydantic_core import CoreSchema, core_schema

from .utils import current_datetime


class Event(BaseModel, ABC):
    """Базовая модель доменного события.

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


class Entity(BaseModel, ABC):
    """Базовая модель для доменной сущности"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=current_datetime)


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
        self.__events.append(event)

    def collect_events(self) -> Iterator[EventT]:
        """Собирает и возвращает все накопленные события"""
        while self.__events:
            yield self.__events.pop(0)


class BaseStrPrimitive(str, ABC):  # noqa: SLOT000
    """Базовый класс для реализации строкового примитива.
    Для создания логики валидации нужно реализовать метод `validate`.
    """

    def __new__(cls, value: str) -> Self:
        value = cls.validate(value)
        return super().__new__(cls, value)

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> str:
        """Логика валидации и проверки значений строки"""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )
