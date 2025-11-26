from abc import ABC, abstractmethod
from datetime import timedelta

from pydantic import BaseModel


class KeyValueCache[T: BaseModel](ABC):
    @abstractmethod
    async def get(self, key: str) -> T | None:
        """Получение данных из кеша"""

    @abstractmethod
    async def set(self, key: str, value: T, ttl: timedelta | None = None) -> None:
        """Добавление данных в кеш"""

    @abstractmethod
    async def invalidate(self, key: str) -> bool:
        """Удаление данных из кеша"""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Проверка наличие данных в кеше"""

    @abstractmethod
    async def clear(self) -> None:
        """Отчистка всех данных в кеше"""
