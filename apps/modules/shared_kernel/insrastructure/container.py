from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from config.dev import settings

from ..application import Storage, UnitOfWork
from .database import SQLAlchemyUnitOfWork, sessionmaker
from .storage import S3Storage


class SharedKernelProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterator[AsyncSession]:  # noqa: PLR6301
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_uow(self, session: AsyncSession) -> UnitOfWork:  # noqa: PLR6301
        return SQLAlchemyUnitOfWork(session)

    @provide(scope=Scope.APP)
    def provide_storage(self) -> Storage:  # noqa: PLR6301
        return S3Storage(
            endpoint_url=settings.minio.url,
            bucket=settings.minio.bucket,
            access_key=settings.minio.user,
            secret_key=settings.minio.password,
        )
