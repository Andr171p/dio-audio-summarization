from typing import Any, Self

from abc import ABC, abstractmethod
from collections import UserString
from collections.abc import Callable

from pydantic_core import CoreSchema, core_schema


class BaseStrPrimitive(str, ABC):  # noqa: SLOT000
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


class CustomStrPrimitive(UserString):
    def __init__(self, seq: str) -> None:
        super().__init__(seq)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, value: str) -> str: pass

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


class Filepath(BaseStrPrimitive):
    """Кастомный примитив для валидации файловых путей.

    Валидирует синтаксис пути без проверки существования файла.
    Поддерживает относительные и абсолютные пути для Unix и Windows.
    """

    MAX_FILEPATH_LENGTH = 4096
    WINDOWS_RESERVED_NAMES: tuple[str, ...] = (
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
        "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3",
        "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    )

    @classmethod
    def validate(cls, filepath: str) -> str:
        if not filepath:
            raise ValueError("Filepath cannot be empty!")
        filepath = filepath.replace("\\", "/")  # Нормализация пути
        cls._check_os_rules(filepath)
        return filepath

    @classmethod
    def _check_os_rules(cls, filepath: str) -> None:
        """Проверка базовых правил для OS"""
        if len(filepath) > cls.MAX_FILEPATH_LENGTH:
            raise ValueError(f"""
                Filepath too long!
                Max length {cls.MAX_FILEPATH_LENGTH}, your length is {len(filepath)}.
            """)
        # Проверка каждой части пути
        for part in filepath.split("/"):
            if not part or part in {".", ".."}:
                continue
            without_ext_part = part.split(".")[0].upper()  # Без расширения
            if without_ext_part in cls.WINDOWS_RESERVED_NAMES:
                raise ValueError(f"Reserved filename: {part}")
