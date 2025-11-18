from typing import Self

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import asynccontextmanager
from types import TracebackType


class UnitOfWork(ABC):
    """Абстрактный класс для имплементации паттерна `UnitOfWork`,
    используется для согласованности транзакций.
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Начало транзакции"""

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> None:
        """Базовая реализация, может быть переопределена в дальнейшем"""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    @asynccontextmanager
    async def transactional(self) -> Iterator[Self]:
        """Начало транзакции"""

    @abstractmethod
    async def commit(self) -> None:
        """Фиксация всех изменений в рамках одной транзакции"""

    @abstractmethod
    async def rollback(self) -> None:
        """Откат всех изменений в рамках одной транзакции"""
