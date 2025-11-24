from abc import ABC

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """Базовый иммутабельный объект значения"""

    model_config = ConfigDict(from_attributes=True, frozen=True)
