from typing import NotRequired, TypedDict

from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import AudioCollection, AudioCollectionStatus, AudioRecord


class AudioCollectionUpdate(TypedDict):
    topic: NotRequired[str]
    status: NotRequired[AudioCollectionStatus]


class AudioCollectionRepository(CRUDRepository[AudioCollection]):
    async def update(self, id: UUID, **kwargs: AudioCollectionUpdate) -> AudioCollection: ...  # noqa: A002

    async def get_by_user(
            self, user_id: UUID, page: int, limit: int
    ) -> list[AudioCollection]: ...

    async def add_record(self, record: AudioRecord) -> AudioRecord: ...
