from typing import Self

from collections.abc import Iterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from ...application import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    @asynccontextmanager
    async def transactional(self) -> Iterator[Self]:
        async with self.session.begin():
            yield self

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
