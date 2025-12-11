from uuid import UUID

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    StrNull,
    StrUnique,
    TextNull,
    UUIDField,
)


class MemberModel(Base):
    __tablename__ = "members"

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), unique=False)
    user_id: Mapped[UUIDField]
    role: Mapped[str]
    status: Mapped[str]
    invited_by: Mapped[StrNull]

    workspace: Mapped["WorkspaceModel"] = relationship(back_populates="members")


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

    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="workspace", lazy="selectin"
    )

    @hybrid_property
    def members_count(self) -> int:
        return len(self.members) if self.members else 0

    @members_count.expression
    def members_count(cls):
        return (
            select([func.count(MemberModel.id)])
            .where(MemberModel.workspace_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
            .label("members_count")
        )
