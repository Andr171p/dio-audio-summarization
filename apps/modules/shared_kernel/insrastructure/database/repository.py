from typing import Protocol

from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain import Entity
from .base import Base


class SQLCRUDRepository[EntityT: Entity, ModelT: Base](Protocol):
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
        except IntegrityError:
            ...
        except SQLAlchemyError:
            ...

    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.entity.model_validate(model) if model else None
        except SQLAlchemyError:
            ...

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
        except IntegrityError:
            ...
        except SQLAlchemyError:
            ...

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError:
            ...
        else:
            return result.rowcount > 0
