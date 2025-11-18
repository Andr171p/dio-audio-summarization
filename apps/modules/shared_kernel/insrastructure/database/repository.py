from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.exceptions import (
    CreationError,
    DeleteError,
    DuplicateError,
    ReadingError,
    UpdateError,
)
from ...domain import Entity
from .base import Base


class SQLAlchemyRepository[EntityT: Entity, ModelT: Base]:
    entity: type[EntityT]
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: EntityT) -> EntityT:
        try:
            stmt = insert(self.model).values(**entity.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            return self.entity.model_validate(model)
        except IntegrityError as e:
            raise DuplicateError(entity_name=self.entity.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            raise CreationError(entity_name=self.entity.__name__, original_error=e) from e

    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.entity.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e

    async def update(self, id: UUID, **kwargs) -> EntityT | None:  # noqa: A002
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**kwargs)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.entity.model_validate(model) if model else None
        except IntegrityError as e:
            raise DuplicateError(entity_name=self.entity.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            raise UpdateError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DeleteError(
                entity_id=id, entity_name=self.entity.__name__, original_error=e
            ) from e
        else:
            return result.rowcount > 0
