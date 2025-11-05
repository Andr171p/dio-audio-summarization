from typing import TypedDict

from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import AudioCollection, AudioRecord


class AudioCollectionUpdate(TypedDict):
    topic: str


class AudioCollectionRepository(CRUDRepository[AudioCollection]):
    async def update(self, id: UUID, **kwargs: AudioCollectionUpdate) -> AudioCollection: ...  # noqa: A002

    async def get_by_user(
            self, user_id: UUID, page: int, limit: int
    ) -> list[AudioCollection]: ...

    async def add_record(self, record: AudioRecord) -> AudioRecord: ...
