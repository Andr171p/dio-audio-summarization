from abc import ABC

from pydantic import BaseModel, ConfigDict, NonNegativeInt


class DTO(BaseModel, ABC):
    """Базовый класс для создания Data Transfer Object - DTO

    DTO не должны содержать доменную логику и сложную валидацию (просто контейнер для данных)
    """

    model_config = ConfigDict(from_attributes=True, frozen=True)


class Pagination(DTO):
    """Пагинация"""

    page: NonNegativeInt
    limit: NonNegativeInt

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
