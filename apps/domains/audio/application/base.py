from typing import TypedDict

from uuid import UUID

from domains.shared_kernel.application import CRUDRepository

from ..domain.aggregates import AudioCollection


class AudioCollectionUpdate(TypedDict):
    topic: str


class AudioCollectionRepository(CRUDRepository[AudioCollection]):
    async def update(self, id: UUID, **kwargs: AudioCollectionUpdate) -> AudioCollection: ...  # noqa: A002

    async def get_by_user(
            self, user_id: UUID, page: int, limit: int
    ) -> list[AudioCollection]: ...
