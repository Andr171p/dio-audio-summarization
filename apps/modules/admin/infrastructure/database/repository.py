from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import WorkspaceRepository
from ...domain import Workspace
from .models import WorkspaceModel


class WorkspaceDataMapper(DataMapper[Workspace, WorkspaceModel]):
    @classmethod
    def model_to_entity(cls, model: WorkspaceModel) -> Workspace:
        return Workspace.model_validate(model)

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
            members_count=entity.members_count,
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

    async def add_member(self) -> ...: ...
