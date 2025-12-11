from typing import Any, Self

from abc import abstractmethod
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from ..domain import EventT
from ..utils import current_datetime
from .repositories import CRUDRepository


class OutboxStatus(StrEnum):
    """Статус выполнения исходящего события"""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class OutboxMessage(BaseModel):
    """Исходящее сообщение"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    message_type: str
    entity_id: UUID
    entity_type: str
    payload: dict[str, Any]
    status: OutboxStatus
    attempts: NonNegativeInt
    max_attempts: NonNegativeInt
    last_error: str | None = None
    occurred_on: datetime = Field(default_factory=current_datetime)
    processed_at: datetime | None = None

    @classmethod
    def create(
            cls, entity_id: UUID, entity_type: str, event: EventT, max_attempts: int = 3
    ) -> Self:
        return cls(
            message_type=event.event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            payload=event.model_dump(),
            status=OutboxStatus.PENDING,
            max_attempts=max_attempts,
        )

    def mark_processed(self) -> None:
        """Отметить успешно обработанное событие"""

        self.status = OutboxStatus.PROCESSED
        self.attempts += 1
        self.processed_at = current_datetime()

    def mark_failed(self, error: str) -> None:
        """Событие завершилось с ошибкой"""

        self.status = OutboxStatus.FAILED
        self.attempts += 1
        self.last_error = error

    def can_retry(self) -> bool:
        """Можно ли повторить обработку события"""

        return self.attempts < self.max_attempts and self.status != OutboxStatus.PROCESSED


class OutboxRepository(CRUDRepository[OutboxMessage]):
    @abstractmethod
    async def get_by_status(
            self, message_type: str, status: OutboxStatus, page: int, limit: int,
    ) -> list[OutboxMessage]:
        """Получение сообщений с их типу и статусу"""

    @abstractmethod
    async def refresh(self, message: OutboxMessage) -> None:
        """Обновляет существующее событие"""
