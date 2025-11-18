from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from ..application import TaskRepository, TranscriptionRepository
from .database import SQLAlchemyTaskRepository, SQLAlchemyTranscriptionRepository


class SummarizationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_task_repo(self, session: AsyncSession) -> TaskRepository:  # noqa: PLR6301
        return SQLAlchemyTaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_transcription_repo(self, session: AsyncSession) -> TranscriptionRepository:  # noqa: PLR6301
        return SQLAlchemyTranscriptionRepository(session)
