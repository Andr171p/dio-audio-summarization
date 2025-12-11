from abc import abstractmethod
from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import Member, Workspace


class WorkspaceRepository(CRUDRepository[Workspace]):
    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]: ...

    @abstractmethod
    async def add_member(self, member: Member) -> Member: ...
