from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import Storage
from modules.shared_kernel.application.eventbus import PrintEventBus

from ..application import (
    CollectionRepository,
    CreateCollectionUseCase,
    UploadRecordUseCase,
)
from .database import SQLCollectionRepository


class AudioProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_collection_repo(self, session: AsyncSession) -> CollectionRepository:  # noqa: PLR6301
        return SQLCollectionRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_collection_creation_usecase(  # noqa: PLR6301
            self, repository: CollectionRepository
    ) -> CreateCollectionUseCase:
        return CreateCollectionUseCase(repository)

    @provide(scope=Scope.REQUEST)
    def provide_record_uploading_usecase(  # noqa: PLR6301
            self, repository: CollectionRepository, storage: Storage
    ) -> UploadRecordUseCase:
        return UploadRecordUseCase(
            repository=repository, storage=storage, eventbus=PrintEventBus()
        )
