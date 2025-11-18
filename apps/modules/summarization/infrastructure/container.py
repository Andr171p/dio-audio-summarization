from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.audio.application import CollectionRepository
from modules.shared_kernel.application.message_bus import LogMessageBus

from ..application import CreateTaskUseCase, TaskRepository, TranscriptionRepository
from .database import SQLAlchemyTaskRepository, SQLAlchemyTranscriptionRepository


class SummarizationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_task_repo(self, session: AsyncSession) -> TaskRepository:  # noqa: PLR6301
        return SQLAlchemyTaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_transcription_repo(self, session: AsyncSession) -> TranscriptionRepository:  # noqa: PLR6301
        return SQLAlchemyTranscriptionRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_task_creation_usecase(  # noqa: PLR6301
            self,
            task_repository: TaskRepository,
            collection_repository: CollectionRepository,
    ) -> CreateTaskUseCase:
        return CreateTaskUseCase(
            task_repository=task_repository,
            collection_repository=collection_repository,
            message_bus=LogMessageBus(),
        )
