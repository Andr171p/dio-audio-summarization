from modules.shared_kernel.application import MessageBus, UnitOfWork

from ..domain import CreateWorkspaceCommand, Workspace
from .repository import WorkspaceRepository


class CreateWorkspaceUseCase:
    def __init__(
            self, uow: UnitOfWork, repository: WorkspaceRepository, message_bus: MessageBus
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._message_bus = message_bus

    async def execute(self, command: CreateWorkspaceCommand) -> Workspace:
        async with self._uow.transactional() as uow:
            workspace = Workspace.create(command)
            await self._repository.create(workspace)
            await uow.commit()
        for event in workspace.collect_events():
            await self._message_bus.send(event)
        return workspace
