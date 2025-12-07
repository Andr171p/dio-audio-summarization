from typing import TypeVar

from abc import ABC

from pydantic import BaseModel, ConfigDict, Field

from ..utils import generate_correlation_id


class Command(BaseModel, ABC):
    """Абстрактный класс для создания команды.
    Команда - инициация определённого действия на уровне приложения, которое изменяет состояние
    или инициирует действие, пример: CreateCollectionCommand (создание аудио коллекции)
    """

    correlation_id: str = Field(default_factory=generate_correlation_id)

    model_config = ConfigDict(from_attributes=True, frozen=True)


class Query(Command, ABC):
    """Запрос - получение или чтение данных не изменяющее состояние приложения"""


CommandT = TypeVar("CommandT", bound=Command)
QueryT = TypeVar("QueryT", bound=Query)
