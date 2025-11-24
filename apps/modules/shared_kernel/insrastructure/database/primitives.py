from typing import Annotated, Any

from datetime import datetime
from uuid import UUID

from sqlalchemy import ARRAY, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column

StrNull = Annotated[str | None, mapped_column(nullable=True)]
StrArray = Annotated[list[str], mapped_column(ARRAY(String))]
StrUnique = Annotated[str, mapped_column(unique=True)]
StrUniqueNull = Annotated[str, mapped_column(unique=True, nullable=True)]
StrText = Annotated[str, mapped_column(Text, nullable=False)]
TextNull = Annotated[str | None, mapped_column(Text, nullable=True)]
UUIDField = Annotated[UUID, mapped_column(PG_UUID(as_uuid=True), unique=False)]
UUIDFieldNull = Annotated[
    UUID | None, mapped_column(PG_UUID(as_uuid=True), unique=True, nullable=True)
]
DateTimeNull = Annotated[datetime | None, mapped_column(DateTime, nullable=True)]
JsonField = Annotated[dict[str, Any], mapped_column(JSONB)]
JsonFieldNull = Annotated[dict[str, Any], mapped_column(JSONB, nullable=True)]
