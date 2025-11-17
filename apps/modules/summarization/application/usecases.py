from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.audio.application import CollectionRepository

from modules.shared_kernel.application import MessageBus

from ..domain import SummarizationTask
from ..domain.commands import CreateSummarizationTaskCommand
from .repositories import TaskRepository


class CreateSummarizationTaskUseCase:
    def __init__(
            self,
            task_repository: TaskRepository,
            collection_repository: "CollectionRepository",
            message_bus: MessageBus,
    ) -> None:
        self.task_repository = task_repository
        self.collection_repository = collection_repository
        self.message_bus = message_bus

    async def execute(self, command: CreateSummarizationTaskCommand) -> SummarizationTask:
        collection = await self.collection_repository.read(command.collection_id)
        task = SummarizationTask.create(
            collection_id=collection.id,
            total_duration=collection.total_duration,
            summary_format=command.summary_format,
            summary_type=command.summary_type,
        )
        created_task = await self.task_repository.create(task)
        for event in task.collect_events():
            await self.message_bus.publish(event)
        return created_task


class AddSummaryTemplateUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, command: ...) -> ...: ...
