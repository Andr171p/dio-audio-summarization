import logging
from datetime import timedelta

from pydantic import BaseModel

from ...application import KeyValueCache

logger = logging.getLogger(__name__)


class InMemoryKeyValueCache[T: BaseModel](KeyValueCache):
    model: type[T]

    def __init__(self, prefix: str) -> None:
        self._cache: dict[str, T] = {}
        self.prefix = prefix

    def _build_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> T | None:
        built_key = self._build_key(key)
        return self._cache.get(built_key)

    async def set(self, key: str, value: T, ttl: timedelta | None = None) -> None:  # noqa: ARG002
        built_key = self._build_key(key)
        self._cache[built_key] = value

    async def invalidate(self, key: str) -> bool:
        built_key = self._build_key(key)
        value = self._cache.pop(built_key, None)
        logger.info("Cache invalidated", extra={"key": built_key})
        return bool(value)

    async def exists(self, key: str) -> bool:
        built_key = self._build_key(key)
        value = self._cache.get(built_key, None)
        return bool(value)

    async def clear(self) -> None:
        for key in list(self._cache.keys()):
            self._cache.pop(key)
        logger.info("Cache cleared successfully!")
