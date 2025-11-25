from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from modules.shared_kernel.application.exceptions import (
    ConflictError,
    CreationError,
    DeleteError,
    ReadingError,
    UpdateError,
)

from ...application import CollectionRepository, CollectionUpdate
from ...domain import (
    AudioCollection,
    AudioFileMetadata,
    AudioRecord,
    CollectionStatus,
)
from .models import AudioCollectionModel, AudioRecordModel


class SQLCollectionRepository(CollectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _map_model_to_collection(model: AudioCollectionModel) -> AudioCollection:
        return AudioCollection(
            id=model.id,
            user_id=model.user_id,
            topic=model.topic,
            status=CollectionStatus(model.status),
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
                    record_metadata=record.metadata.model_dump(mode="json")
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
            raise ConflictError(
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

    async def update(self, id: UUID, **kwargs: CollectionUpdate) -> AudioCollection | None:  # noqa: A002
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
            raise ConflictError(
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
                record_metadata=record.metadata.model_dump(mode="json"),
                created_at=record.created_at,
            )
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return AudioRecord(
                id=model.id,
                collection_id=model.collection_id,
                filepath=model.filepath,
                metadata=AudioFileMetadata.model_validate(model.record_metadata),
                created_at=model.created_at,
            )
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(entity_name=AudioRecord.__name__, original_error=e) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(entity_name=AudioRecord.__name__, original_error=e) from e

    async def get_record(self, record_id: UUID) -> AudioRecord | None:
        try:
            stmt = select(AudioRecordModel).where(AudioRecordModel.id == record_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return AudioRecord(
                id=model.id,
                collection_id=model.collection_id,
                filepath=model.filepath,
                metadata=AudioFileMetadata.model_validate(model.record_metadata),
                created_at=model.created_at,
            )
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=AudioRecord.__name__, entity_id=record_id, original_error=e
            ) from e

    async def get_by_user_id(self, user_id: UUID, page: int, limit: int) -> list[AudioCollection]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(AudioCollectionModel)
                .where(AudioCollectionModel.user_id == user_id)
                .order_by(AudioCollectionModel.created_at)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self._map_model_to_collection(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=AudioCollection.__name__, entity_id=user_id, original_error=e
            ) from e
