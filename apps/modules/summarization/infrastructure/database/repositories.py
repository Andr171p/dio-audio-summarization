from modules.shared_kernel.insrastructure.database import SQLCRUDRepository

from ...application import TaskRepository, TranscriptionRepository
from ...domain import SummarizationTask, Transcription
from .models import SummarizationTaskModel, TranscriptionModel


class SQLTaskRepository(
    SQLCRUDRepository[SummarizationTask, SummarizationTaskModel], TaskRepository
):
    pass


class SQLTranscriptionRepository(
    SQLCRUDRepository[Transcription, TranscriptionModel],
    TranscriptionRepository,
):
    pass
