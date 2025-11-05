from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from modules.shared_kernel.application.exceptions import (
    CreationError,
    DeleteError,
    DuplicateError,
    ReadingError,
    UpdateError,
)

from ...application import AudioCollectionRepository, AudioCollectionUpdate
from ...domain import (
    AudioCollection,
    AudioCollectionStatus,
    AudioFileMetadata,
    AudioRecord,
)
from .models import AudioCollectionModel, AudioRecordModel


class SQLAudioCollectionRepository(AudioCollectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _map_model_to_collection(model: AudioCollectionModel) -> AudioCollection:
        return AudioCollection(
            id=model.id,
            user_id=model.user_id,
            topic=model.topic,
            status=AudioCollectionStatus(model.status),
            record_count=model.record_count,
            created_at=model.created_at,
            records=[
                AudioRecord(
                    id=record.id,
                    collection_id=record.collection_id,
                    filepath=record.filepath,
                    metadata=AudioFileMetadata.model_validate(record.record_metadata),
                    created_at=record.created_at,
                )
                for record in model.records
            ]
        )

    async def create(self, collection: AudioCollection) -> AudioCollection:
        try:
            collection_model = AudioCollectionModel(**collection.model_dump(exclude={"records"}))
            self.session.add(collection_model)
            await self.session.flush()
            record_models = [
                AudioRecordModel(
                    collection_id=collection_model.id,
                    filepath=record.filepath,
                    record_metadata=record.metadata.model_dump()
                )
                for record in collection.records
            ]
            self.session.add_all(record_models)
            await self.session.flush()
            await self.session.refresh(collection_model, ["records"])
            await self.session.commit()
            return self._map_model_to_collection(collection_model)
        except IntegrityError as e:
            await self.session.rollback()
            raise DuplicateError(
                entity_name=AudioCollection.__name__, original_error=e
            ) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(
                entity_name=AudioCollection.__name__, original_error=e
            ) from e

    async def read(self, id: UUID) -> AudioCollection | None:  # noqa: A002
        try:
            stmt = (
                select(AudioCollectionModel)
                .options(joinedload(AudioCollectionModel.records))
                .where(AudioCollectionModel.id == id)
            )
            result = await self.session.execute(stmt)
            model = result.unique().scalar_one_or_none()
            if model is None:
                return None
            return self._map_model_to_collection(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=AudioCollection.__name__, entity_id=id, original_error=e
            ) from e

    async def update(self, id: UUID, **kwargs: AudioCollectionUpdate) -> AudioCollection | None:  # noqa: A002
        try:
            stmt = (
                update(AudioCollectionModel)
                .where(AudioCollectionModel.id == id)
                .values(**kwargs)
                .returning(AudioCollectionModel)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            model = result.unique().scalar_one_or_none()
            return AudioCollection.model_validate(model) if model is not None else None
        except IntegrityError as e:
            await self.session.rollback()
            raise DuplicateError(
                entity_name=AudioCollection.__name__, original_error=e
            ) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(
                entity_name=AudioCollection.__name__,
                entity_id=id,
                original_error=e,
                details=kwargs,
            ) from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(AudioCollectionModel).where(AudioCollectionModel.id == id)
            result = await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeleteError(
                entity_name=AudioCollection.__name__, entity_id=id, original_error=e
            ) from e
        else:
            return result.rowcount > 0

    async def add_record(self, record: AudioRecord) -> AudioRecord:
        try:
            model = AudioRecordModel(
                id=record.id,
                collection_id=record.collection_id,
                filepath=record.filepath,
                record_metadata=record.metadata.model_dump(),
                created_at=record.created_at,
            )
            self.session.add(model)
            await self.session.commit()
            return AudioRecord.model_validate(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise DuplicateError(entity_name=AudioRecord.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(entity_name=AudioRecord.__name__, original_error=e) from e
