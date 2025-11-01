from typing import Protocol, TypeVar

from uuid import UUID

from pydantic import BaseModel

from .domain import File, Filepath
from .domain.events import EventT

T = TypeVar("T", bound=BaseModel)


class EventBus(Protocol):
    async def publish(self, event: EventT, **kwargs) -> None: ...


class WritableRepository[T: BaseModel](Protocol):
    async def create(self, entity: T) -> T: ...

    async def update(self, id: UUID, **kwargs) -> T: ...  # noqa: A002

    async def delete(self, id: UUID) -> bool: ...  # noqa: A002


class ReadableRepository[T: BaseModel](Protocol):
    async def read(self, id: UUID) -> T | None: ...  # noqa: A002

    async def read_all(self, page: int, limit: int) -> list[T]: ...


class CRUDRepository(WritableRepository[T], ReadableRepository[T]):
    pass


class Storage(Protocol):
    async def upload(self, file: File) -> None: ...

    async def download(self, filepath: Filepath) -> File | None: ...

    async def remove(self, filepath: Filepath) -> bool: ...

    async def exists(self, filepath: Filepath) -> bool: ...
