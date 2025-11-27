from abc import ABC

from pydantic import BaseModel, ConfigDict


class DTO(BaseModel, ABC):
    """Базовый класс для создания Data Transfer Object - DTO

    DTO не должны содержать доменную логику и сложную валидацию (просто контейнер для данных)
    """

    model_config = ConfigDict(from_attributes=True, frozen=True)
