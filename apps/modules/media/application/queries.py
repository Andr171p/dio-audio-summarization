from uuid import UUID

from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import Query

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 5  # 5 MB
MAX_CHUNK_SIZE = 1024 * 1024 * 100


class DownloadFileQuery(Query):
    file_id: UUID
    chunk_size: PositiveInt = Field(default=DEFAULT_CHUNK_SIZE, le=MAX_CHUNK_SIZE)
