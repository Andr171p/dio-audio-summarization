from datetime import datetime

from sqlalchemy import DateTime, UniqueConstraint, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column

from ...application import OutboxMessage, OutboxRepository, OutboxStatus, Pagination
from ...application.exceptions import ReadingError
from .base import Base
from .primitives import DateTimeNull, JsonField, StrNull, UUIDField
from .repository import DataMapper, SQLAlchemyRepository


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    message_type: Mapped[str]
    entity_id: Mapped[UUIDField]
    entity_type: Mapped[str]
    payload: Mapped[JsonField]
    status: Mapped[str]
    attempts: Mapped[int]
    max_attempts: Mapped[int]
    last_error: Mapped[StrNull]
    occurred_on: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[DateTimeNull]

    __table_args__ = (
        UniqueConstraint("entity_id", "entity_type", "payload", name="outbox_uq"),
    )


class OutboxDataMapper(DataMapper[OutboxMessage, OutboxMessageModel]):
    @classmethod
    def model_to_entity(cls, model: OutboxMessageModel) -> OutboxMessage:
        return OutboxMessage.model_validate(model)

    @classmethod
    def entity_to_model(cls, entity: OutboxMessage) -> OutboxMessageModel:
        return OutboxMessageModel(**entity.model_dump())


class SQLAlchemyOutboxRepository(
    SQLAlchemyRepository[OutboxMessage, OutboxMessageModel], OutboxRepository
):
    entity = OutboxMessage
    model = OutboxMessageModel
    data_mapper = OutboxDataMapper

    async def get_by_status(
        self, status: OutboxStatus, pagination: Pagination,
    ) -> list[OutboxMessage]:
        try:
            conditions = (
                (self.model.status == status) &
                (self.model.attempts <= self.model.max_attempts)
            )
            stmt = (
                select(self.model)
                .where(conditions)
                .order_by(self.model.occurred_on.asc())
                .offset(pagination.offset)
                .limit(pagination.limit)
                .with_for_update(skip_locked=True)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.data_mapper.model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__,
                entity_id=status.value(),
                details={"status": status},
                original_error=e
            ) from e
