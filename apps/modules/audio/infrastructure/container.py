from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.shared_kernel.application import Storage
from modules.shared_kernel.application.eventbus import PrintEventBus

from ..application import (
    AddAudioRecordUseCase,
    AudioCollectionRepository,
    CreateAudioCollectionUseCase,
    SummarizeAudioCollectionUseCase,
)
from .database import SQLAudioCollectionRepository


class AudioProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_collection_repo(self, session: AsyncSession) -> AudioCollectionRepository:  # noqa: PLR6301
        return SQLAudioCollectionRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_collection_creation_usecase(  # noqa: PLR6301
            self, repository: AudioCollectionRepository
    ) -> CreateAudioCollectionUseCase:
        return CreateAudioCollectionUseCase(repository)

    @provide(scope=Scope.REQUEST)
    def provide_record_addition_usecase(  # noqa: PLR6301
            self, repository: AudioCollectionRepository, storage: Storage
    ) -> AddAudioRecordUseCase:
        return AddAudioRecordUseCase(
            repository=repository, storage=storage, eventbus=PrintEventBus()
        )

    @provide(scope=Scope.REQUEST)
    def provide_collection_summarization_usecase(  # noqa: PLR6301
            self, repository: AudioCollectionRepository
    ) -> SummarizeAudioCollectionUseCase:
        return SummarizeAudioCollectionUseCase(repository=repository, eventbus=PrintEventBus())
