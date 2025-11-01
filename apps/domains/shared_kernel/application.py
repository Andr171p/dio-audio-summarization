from typing import Protocol, TypeVar

from uuid import UUID

from pydantic import BaseModel

from .domain import File, Filepath
from .domain.events import EventT

T = TypeVar("T", bound=BaseModel)


class EventBus(Protocol):
    """Шина событий (интерфейс-адаптер для брокеров сообщений)"""

    async def publish(self, event: EventT, **kwargs) -> None: pass


class WritableRepository[T: BaseModel](Protocol):
    """Репозиторий для изменения данных"""

    async def create(self, entity: T) -> T: pass

    async def update(self, id: UUID, **kwargs) -> T: pass  # noqa: A002

    async def delete(self, id: UUID) -> bool: pass  # noqa: A002


class ReadableRepository[T: BaseModel](Protocol):
    """Репозиторий для чтения данных"""

    async def read(self, id: UUID) -> T | None: pass  # noqa: A002

    async def read_all(self, page: int, limit: int) -> list[T]: pass


class CRUDRepository(WritableRepository[T], ReadableRepository[T]):
    """Базовые CRUD операции"""


class Storage(Protocol):
    """Файловое/объектное хранилище"""

    async def upload(self, file: File) -> None: pass

    async def download(self, filepath: Filepath) -> File | None: pass

    async def remove(self, filepath: Filepath) -> bool: pass

    async def exists(self, filepath: Filepath) -> bool: pass
