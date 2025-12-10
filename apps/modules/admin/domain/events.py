from typing import ClassVar

from uuid import UUID

from pydantic import HttpUrl

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
