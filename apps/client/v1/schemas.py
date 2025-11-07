from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Collection(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    status: str
    record_count: int
    records: list[dict[str, ...]]
    created_at: datetime
