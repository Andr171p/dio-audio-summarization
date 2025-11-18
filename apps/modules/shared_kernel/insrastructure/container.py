from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from config.dev import settings as dev_settings

from ..application import MessageBus, Storage, UnitOfWork
from .broker import RabbitMQMessageBus, broker
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
            endpoint_url=dev_settings.minio.url,
            bucket=dev_settings.minio.bucket,
            access_key=dev_settings.minio.user,
            secret_key=dev_settings.minio.password,
        )

    @provide(scope=Scope.APP)
    def provide_message_bus(self) -> MessageBus:  # noqa: PLR6301
        return RabbitMQMessageBus(broker)
