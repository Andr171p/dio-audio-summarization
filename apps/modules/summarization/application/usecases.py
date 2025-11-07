from ..domain.commands import CreateSummarizationTaskCommand
from ..domain.entities import SummarizationTask
from ..domain.events import SummarizationStartedEvent


class CreateSummarizationTaskUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, command: CreateSummarizationTaskCommand) -> SummarizationTask:
        ...
