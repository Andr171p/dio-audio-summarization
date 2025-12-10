from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from modules.iam.domain import UserRole

from uuid import UUID

from pydantic import EmailStr, HttpUrl

from modules.shared_kernel.domain import Event

from .value_objects import OrganizationType


class WorkspaceCreatedEvent(Event):
    event_type: ClassVar[str] = "workspace_created"

    workspace_id: UUID
    name: str
    organization_type: OrganizationType
    organization_url: HttpUrl | None
    description: str | None
    use_ai_consultant: bool


class MemberInvitedEvent(Event):
    event_type: ClassVar[str] = "member_invited"

    workspace_id: UUID
    email: EmailStr
    member_role: "UserRole"
    token: str
