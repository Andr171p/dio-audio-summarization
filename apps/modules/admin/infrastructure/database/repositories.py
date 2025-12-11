from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from modules.shared_kernel.application.exceptions import ConflictError, CreationError, ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import WorkspaceRepository
from ...domain import Member, OrganizationType, Workspace, WorkspaceType
from .models import MemberModel, WorkspaceModel


class WorkspaceDataMapper(DataMapper[Workspace, WorkspaceModel]):
    @classmethod
    def model_to_entity(cls, model: WorkspaceModel) -> Workspace:
        return Workspace(
            id=model.id,
            space_type=WorkspaceType(model.space_type),
            owner_id=model.owner_id,
            name=model.name,
            slug=model.slug,
            organization_type=OrganizationType(model.organization_type),
            organization_url=model.organization_url,
            description=model.description,
            use_ai_consultant=model.use_ai_consultant,
            members_count=model.members_count,
            created_at=model.created_at,
        )

    @classmethod
    def entity_to_model(cls, entity: Workspace) -> WorkspaceModel:
        return WorkspaceModel(
            id=entity.id,
            owner_id=entity.owner_id,
            space_type=entity.space_type,
            name=entity.name,
            slug=entity.slug,
            organization_type=entity.organization_type,
            organization_url=str(entity.organization_url),
            description=entity.description,
            use_ai_consultant=entity.use_ai_consultant,
            created_at=entity.created_at,
        )


class MemberDataMapper(DataMapper[Member, MemberModel]):
    @classmethod
    def model_to_entity(cls, model: MemberModel) -> Member:
        return Member.model_validate(model)

    @classmethod
    def entity_to_model(cls, entity: Member) -> MemberModel:
        return MemberModel(
            id=entity.id,
            workspace_id=entity.workspace_id,
            user_id=entity.user_id,
            role=entity.role,
            status=entity.status,
            created_at=entity.created_at,
        )


class SQLAlchemyWorkspaceRepository(
    SQLAlchemyRepository[Workspace, WorkspaceModel], WorkspaceRepository
):
    entity = Workspace
    model = WorkspaceModel
    data_mapper = WorkspaceDataMapper

    async def get_by_owner(self, owner_id: UUID) -> list[Workspace]:
        try:
            stmt = select(self.model).where(self.model.owner_id == owner_id)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.data_mapper.model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__,
                entity_id=owner_id,
                details={"owner_id": owner_id},
                original_error=e
            ) from e

    async def add_member(self, member: Member) -> Member:
        try:
            model = MemberDataMapper.entity_to_model(member)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return MemberDataMapper.model_to_entity(model)
        except IntegrityError as e:
            raise ConflictError(entity_name="Member", original_error=e) from e
        except SQLAlchemyError as e:
            raise CreationError(entity_name="Member", original_error=e) from e
