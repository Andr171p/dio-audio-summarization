from typing import Self

from uuid import UUID

from pydantic import HttpUrl, NonNegativeInt

from modules.shared_kernel.domain import AggregateRoot

from .commands import CreateWorkspaceCommand
from .events import WorkspaceCreatedEvent
from .value_objects import OrganizationType, WorkspaceType


class Workspace(AggregateRoot):
    """Рабочее пространство компании (создаётся админом).

    Attributes:
        owner_id: Идентификатор владельца области.
        space_type: Тип рабочего пространства (может быть 'private', 'public').
        name: Имя области.
        slug: Имя области отображаемое в URL.
        organization_type: Тип организации (обязательно поле).
        organization_url: URL адрес компании (адрес главного сайта).
        description: Описание предметной области.
        use_ai_consultant: Использовать ли AI консультанта для управления рабочим пространством.
        members_count: Количество участников.
    """

    owner_id: UUID
    space_type: WorkspaceType
    name: str
    slug: str
    organization_type: OrganizationType
    organization_url: HttpUrl | None = None
    description: str | None = None
    use_ai_consultant: bool = True
    members_count: NonNegativeInt

    @classmethod
    def create(cls, command: CreateWorkspaceCommand) -> Self:
        """Фабричный метод для создания рабочего пространства"""

        workspace = cls(
            owner_id=command.owner_id,
            space_type=WorkspaceType.PRIVATE,
            name=command.name,
            slug=command.slug,
            organization_type=command.organization_type,
            organization_url=command.organization_url,
            description=command.description,
            members_count=0,
        )
        cls._register_event(workspace, WorkspaceCreatedEvent(
            workspace_id=workspace.id,
            name=workspace.name,
            organization_type=workspace.organization_type,
            organization_url=workspace.organization_url,
            description=workspace.description,
            use_ai_consultant=workspace.use_ai_consultant,
        ))
        return workspace
