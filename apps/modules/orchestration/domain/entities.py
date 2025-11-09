from uuid import UUID

from pydantic import PositiveFloat, PositiveInt

from modules.shared_kernel.domain import Entity


class AudioChunk(Entity):
    collection_id: UUID
    record_id: UUID
    filename: str
    format: str
    chunk_number: PositiveInt
    chunk_size: PositiveInt
    chunk_duration: PositiveFloat
    content: bytes
