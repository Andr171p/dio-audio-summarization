from modules.shared_kernel.application import CRUDRepository

from ..domain import SummarizationTask, Summary, Transcription

SummaryRepository = CRUDRepository[Summary]
TaskRepository = CRUDRepository[SummarizationTask]
TranscriptionRepository = CRUDRepository[Transcription]
