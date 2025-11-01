from typing import ClassVar, TypeVar

from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .utils import current_datetime


class Event(BaseModel, ABC):
    """Базовая модель доменного события"""
    event_id: UUID = Field(default_factory=uuid4)
    event_version: int = Field(default=1)
    event_type: ClassVar[str]
    occurred_on: datetime = Field(default_factory=current_datetime)


EventT = TypeVar("EventT", bound=Event)
