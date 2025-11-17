from typing import Any, Self

from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict
from pydantic_core import CoreSchema, core_schema


class ValueObject(BaseModel, ABC):
    """Базовый иммутабельный объект значения"""

    model_config = ConfigDict(frozen=True)


class StrPrimitive(str, ABC):  # noqa: SLOT000
    """Базовый класс для реализации строкового примитива.
    Для создания логики валидации нужно реализовать метод `validate`.
    """

    def __new__(cls, value: str) -> Self:
        value = cls.validate(value)
        return super().__new__(cls, value)

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> str:
        """Логика валидации и проверки значений строки"""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )
