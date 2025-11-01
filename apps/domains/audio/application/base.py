from uuid import UUID

from ..domain.aggregates import AudioCollection

from domains.shared_kernel.application import WritableRepository


class AudioCollectionRepository(WritableRepository[AudioCollection]):
    async def read(self, id: UUID) -> AudioCollection | None: ...  # noqa: A002
