from typing import TypeVar

from abc import ABC, abstractmethod
from uuid import UUID

from ..domain import Entity

EntityT = TypeVar("EntityT", bound=Entity)


class WritableRepository[EntityT: Entity](ABC):
    """Репозиторий для изменения данных"""

    @abstractmethod
    async def create(self, entity: EntityT) -> EntityT: pass

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> EntityT | None: pass  # noqa: A002

    @abstractmethod
    async def delete(self, id: UUID) -> bool: pass  # noqa: A002


class ReadableRepository[EntityT: Entity](ABC):
    """Репозиторий для чтения данных"""

    @abstractmethod
    async def read(self, id: UUID, **kwargs) -> EntityT | None: pass  # noqa: A002

    @abstractmethod
    async def read_all(self, page: int, limit: int) -> list[EntityT]: pass


class CRUDRepository(WritableRepository[EntityT], ReadableRepository[EntityT], ABC):
    """Базовые CRUD операции"""
