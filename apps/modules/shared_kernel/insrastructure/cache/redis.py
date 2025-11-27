import logging
from datetime import timedelta

from pydantic import BaseModel
from redis import RedisError
from redis.asyncio import Redis

from ...application import KeyValueCache
from ...application.exceptions import CacheHitError, CacheInvalidationError, CacheSetError

logger = logging.getLogger(__name__)


class RedisKeyValueCache[T: BaseModel](KeyValueCache):
    """Базовый класс для реализации кеширования используя Redis backend.
    Поле класса `model` используется для автоматической сериализации
    кешируемого объекта.
    """

    model: type[T]

    def __init__(self, url: str, prefix: str, ttl: timedelta) -> None:
        """
        :param url: URL для подключения к Redis.
        :param prefix: Осмысленный префикс для уникального ключа (для избежания коллизий).
        :param ttl: Время жизни значения в кеше (обязателен для production).
        """

        self.redis = Redis.from_url(url)
        self.prefix = prefix
        self.ttl = ttl

    def _build_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> T | None:
        built_key = self._build_key(key)
        try:
            data = await self.redis.get(built_key)
            if data is None:
                logger.debug("Cache miss", extra={"key": built_key})
                return None
            logger.debug("Cache hit", extra={"key": built_key})
            return self.model.model_validate_json(data.decode("utf-8"))
        except RedisError as e:
            raise CacheHitError(key=built_key, original_error=e) from e

    async def set(self, key: str, value: T, ttl: timedelta | None = None) -> None:
        actual_ttl = ttl or self.ttl
        built_key = self._build_key(key)
        try:
            await self.redis.set(built_key, value.model_dump_json())
            await self.redis.expire(built_key, actual_ttl)
            logger.info(
                "Cache set successfully",
                extra={"key": built_key, "value": value.model_dump_json()}
            )
        except RedisError as e:
            raise CacheSetError(key=built_key, value=value, original_error=e) from e

    async def invalidate(self, key: str) -> bool:
        built_key = self._build_key(key)
        try:
            deleted_keys = await self.redis.delete(built_key)
        except RedisError as e:
            raise CacheInvalidationError(key=built_key, original_error=e) from e
        else:
            logger.info("Cache invalidated", extra={"key": built_key})
            return deleted_keys > 0

    async def exists(self, key: str) -> bool:
        built_key = self._build_key(key)
        return await self.redis.exists(built_key)

    async def clear(self) -> None:
        """Отчистка кеша по префиксу"""

        pattern = f"{self.prefix}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            logger.info("Cleared %s keys with prefix %s", len(keys), self.prefix)
        logger.info("Cache cleared successfully!")
