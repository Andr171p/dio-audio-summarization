from abc import abstractmethod
from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import Invitation, Member, Workspace


class WorkspaceRepository(CRUDRepository[Workspace]):
    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]: ...

    @abstractmethod
    async def get_member(self, workspace_id: UUID, user_id: UUID) -> Member | None: ...

    @abstractmethod
    async def add_member(self, member: Member) -> Member: ...

    @abstractmethod
    async def add_invitation(self, invitation: Invitation) -> Invitation: ...


class InvitationRepository(CRUDRepository[Invitation]):
    @abstractmethod
    async def get_by_token(self, token: str) -> Invitation: ...
