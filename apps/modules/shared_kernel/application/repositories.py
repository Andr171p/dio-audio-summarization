from typing import Protocol, TypeVar

from uuid import UUID

from ..domain import Entity

EntityT = TypeVar("EntityT", bound=Entity)


class WritableRepository[T: Entity](Protocol):
    """Репозиторий для изменения данных"""

    async def create(self, entity: T) -> T: pass

    async def update(self, id: UUID, **kwargs) -> T: pass  # noqa: A002

    async def delete(self, id: UUID) -> bool: pass  # noqa: A002


class ReadableRepository[T: Entity](Protocol):
    """Репозиторий для чтения данных"""

    async def read(self, id: UUID) -> T | None: pass  # noqa: A002

    async def read_all(self, page: int, limit: int) -> list[T]: pass


class CRUDRepository(WritableRepository[EntityT], ReadableRepository[EntityT]):
    """Базовые CRUD операции"""
