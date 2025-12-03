from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import FileMetaRepository
from ...domain import FileMetadata, Filepath
from .models import FileMetadataModel


class FileMetaDataMapper(DataMapper[FileMetadata, FileMetadataModel]):
    entity_class = FileMetadata
    model_class = FileMetadataModel

    def entity_to_model(cls, entity: FileMetadata) -> FileMetadataModel:
        return FileMetadataModel(**entity.model_dump())

    def model_to_entity(cls, model: FileMetadataModel) -> FileMetadata:
        return FileMetadata.model_validate(model)


class SQLAlchemyFileMetaRepository(
    SQLAlchemyRepository[FileMetadata, FileMetadataModel], FileMetaRepository
):
    entity = FileMetadata
    model = FileMetadataModel
    data_mapper = FileMetaDataMapper

    async def get_by_filepath(self, filepath: Filepath) -> FileMetadata | None:
        try:
            stmt = select(self.model).where(self.model.filepath == filepath)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return None if model is None else self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=FileMetadata.__class__.__name__, entity_id=filepath
            ) from e
