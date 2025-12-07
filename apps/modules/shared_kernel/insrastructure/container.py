from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from ..application import UnitOfWork
from .database import SQLAlchemyUnitOfWork, sessionmaker


class SharedKernelProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterator[AsyncSession]:  # noqa: PLR6301
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_uow(self, session: AsyncSession) -> UnitOfWork:  # noqa: PLR6301
        return SQLAlchemyUnitOfWork(session)
