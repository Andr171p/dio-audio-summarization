from sqlalchemy.orm import Mapped

from modules.shared_kernel.insrastructure.database import (
    Base,
    StrNull,
    StrUnique,
    TextNull,
    UUIDField,
)


class WorkspaceModel(Base):
    __tablename__ = "workspaces"

    owner_id: Mapped[UUIDField]
    space_type: Mapped[str]
    name: Mapped[str]
    slug: Mapped[StrUnique]
    organization_type: Mapped[str]
    organization_url: Mapped[StrNull]
    description: Mapped[TextNull]
    use_ai_consultant: Mapped[bool]
    members_count: Mapped[int]
