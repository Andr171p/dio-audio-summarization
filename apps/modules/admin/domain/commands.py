from uuid import UUID

from pydantic import HttpUrl

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
