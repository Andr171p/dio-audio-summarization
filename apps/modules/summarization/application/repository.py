from modules.shared_kernel.application import CRUDRepository

from ..domain import SummarizationTask

TaskRepository = CRUDRepository[SummarizationTask]
