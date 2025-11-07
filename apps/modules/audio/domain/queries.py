from uuid import UUID

from pydantic import BaseModel, PositiveInt


class DownloadRecordQuery(BaseModel):
    collection_id: UUID
    record_id: UUID
    chunk_size: PositiveInt
