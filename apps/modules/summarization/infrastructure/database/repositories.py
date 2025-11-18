from modules.shared_kernel.insrastructure.database import SQLAlchemyRepository

from ...application import TaskRepository, TranscriptionRepository
from ...domain import SummarizationTask, Transcription
from .models import SummarizationTaskModel, TranscriptionModel


class SQLAlchemyTaskRepository(
    SQLAlchemyRepository[SummarizationTask, SummarizationTaskModel], TaskRepository
):
    pass


class SQLAlchemyTranscriptionRepository(
    SQLAlchemyRepository[Transcription, TranscriptionModel],
    TranscriptionRepository,
):
    pass
