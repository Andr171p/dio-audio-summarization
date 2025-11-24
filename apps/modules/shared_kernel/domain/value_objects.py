from abc import ABC

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """Базовый иммутабельный объект значения"""

    model_config = ConfigDict(frozen=True)
