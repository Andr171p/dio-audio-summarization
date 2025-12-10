from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.iam.domain import UserRole

from uuid import UUID

from pydantic import EmailStr, HttpUrl

from modules.shared_kernel.domain import Command

from .value_objects import OrganizationType


class CreateWorkspaceCommand(Command):
    """Команда для создания рабочей области"""

    owner_id: UUID
    name: str
    slug: str
    description: str | None = None
    organization_type: OrganizationType
    organization_url: HttpUrl | None = None


class InviteMemberCommand(Command):
    """Команда для приглашения участника в рабочее пространство"""

    workspace_id: UUID
    email: EmailStr
    member_role: "UserRole"
