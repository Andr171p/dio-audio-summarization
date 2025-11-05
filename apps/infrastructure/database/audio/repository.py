from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from domains.audio.domain import (
    AudioCollection,
    AudioCollectionStatus,
    AudioFileMetadata,
    AudioRecord,
)
from domains.audio.repositories import AudioCollectionRepository, AudioCollectionUpdate

from .models import AudioCollectionModel, AudioRecordModel


class SQLAudioCollectionRepository(AudioCollectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _map_model_collection(model: AudioCollectionModel) -> AudioCollection:
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
            await self.session.commit()
            return self._map_model_collection(collection_model)
        except IntegrityError:
            ...
        except SQLAlchemyError:
            ...

    async def read(self, id: UUID) -> AudioCollectionModel | None:  # noqa: A002
        try:
            stmt = select(AudioCollectionModel).where(AudioCollectionModel.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return AudioCollection.model_validate(model) if model is not None else None
        except SQLAlchemyError:
            ...

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
            model = result.scalar_one_or_none()
            return AudioCollection.model_validate(model) if model is not None else None
        except IntegrityError:
            ...
        except SQLAlchemyError:
            ...

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(AudioCollectionModel).where(AudioCollectionModel.id == id)
            result = await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError:
            ...
        else:
            return result.rowcount > 0

    async def add_record(self, record: AudioRecord) -> AudioRecord:
        try:
            model = AudioRecordModel(**record.model_dump())
            self.session.add(model)
            await self.session.commit()
            return AudioRecord.model_validate(model)
        except IntegrityError:
            ...
        except SQLAlchemyError:
            ...
