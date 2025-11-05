from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import Base, DictJson, PostgresUUID, StrUnique


class AudioCollectionModel(Base):
    __tablename__ = "audio_collections"

    user_id: Mapped[PostgresUUID]
    topic: Mapped[StrUnique]
    status: Mapped[str]
    record_count: Mapped[int]

    records: Mapped[list["AudioRecordModel"]] = relationship(back_populates="collection")

    __table_args__ = (
        CheckConstraint("record_count > 0", name="check_record_count"),
    )


class AudioRecordModel(Base):
    __tablename__ = "audio_records"

    collection_id: Mapped[UUID] = mapped_column(
        ForeignKey("audio_collections.id"), unique=False
    )
    filepath: Mapped[StrUnique]
    record_metadata: Mapped[DictJson]

    collection: Mapped["AudioCollectionModel"] = relationship(back_populates="records")
