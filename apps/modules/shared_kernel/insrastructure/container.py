from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from config.dev import settings as dev_settings

from ..application import Storage
from .database import sessionmaker
from .storage import S3Storage


class SharedProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterator[AsyncSession]:  # noqa: PLR6301
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def provide_storage(self) -> Storage:  # noqa: PLR6301
        return S3Storage(
            endpoint_url=dev_settings.minio.url,
            bucket=dev_settings.minio.bucket,
            access_key=dev_settings.minio.user,
            secret_key=dev_settings.minio.password,
        )
