from typing import Self

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import asynccontextmanager


class UnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> Iterator[Self]: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
