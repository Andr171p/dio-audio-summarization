from typing import NotRequired, TypedDict

from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import AudioCollection, AudioRecord, CollectionStatus


class CollectionUpdate(TypedDict):
    topic: NotRequired[str]
    status: NotRequired[CollectionStatus]


class CollectionRepository(CRUDRepository[AudioCollection]):
    async def update(self, id: UUID, **kwargs: CollectionUpdate) -> AudioCollection: ...  # noqa: A002

    async def get_by_user(
            self, user_id: UUID, page: int, limit: int
    ) -> list[AudioCollection]: ...

    async def add_record(self, record: AudioRecord) -> AudioRecord: ...

    async def get_record(self, collection_id: UUID, record_id: UUID) -> AudioRecord | None:
        """Два аргумента для проверки принадлежности"""
