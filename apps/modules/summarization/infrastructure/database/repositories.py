from modules.shared_kernel.insrastructure.database import SQLAlchemyRepository

from ...application import TaskRepository, TranscriptionRepository
from ...domain import SummarizationTask, Transcription
from .models import SummarizationTaskModel, TranscriptionModel


class SQLAlchemyTaskRepository(
    SQLAlchemyRepository[SummarizationTask, SummarizationTaskModel], TaskRepository
):
    entity = SummarizationTask
    model = SummarizationTaskModel


class SQLAlchemyTranscriptionRepository(
    SQLAlchemyRepository[Transcription, TranscriptionModel],
    TranscriptionRepository,
):
    entity = Transcription
    model = TranscriptionModel
