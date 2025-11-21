from typing import Annotated, Any, Final

from collections.abc import AsyncIterator
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config.dev import settings as dev_settings

engine: Final[AsyncEngine] = create_async_engine(
    url=dev_settings.postgres.sqlalchemy_url, echo=True
)
sessionmaker: Final[async_sessionmaker[AsyncSession]] = async_sessionmaker(
    engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)

StrNullable = Annotated[str | None, mapped_column(nullable=True)]
StringArray = Annotated[list[str], mapped_column(ARRAY(String))]
StrUnique = Annotated[str, mapped_column(unique=True)]
StrUniqueNullable = Annotated[str, mapped_column(unique=True, nullable=True)]
StrText = Annotated[str, mapped_column(Text, nullable=False)]
TextNullable = Annotated[str | None, mapped_column(Text, nullable=True)]
UUIDField = Annotated[UUID, mapped_column(PG_UUID(as_uuid=True), unique=False)]
UUIDFieldNullable = Annotated[
    UUID | None, mapped_column(PG_UUID(as_uuid=True), unique=True, nullable=True)
]
DatetimeNullable = Annotated[datetime | None, mapped_column(DateTime, nullable=True)]
JsonField = Annotated[dict[str, Any], mapped_column(JSONB)]
JsonFieldNullable = Annotated[dict[str, Any], mapped_column(JSONB, nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


async def session_factory() -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
