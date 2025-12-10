from pydantic import Field

from modules.shared_kernel.application import DTO

from ..domain import OrganizationType


class WorkspaceCreate(DTO):
    name: str = Field(..., description="Название области")
    slug: str = Field(..., description="Уникальная строка для URL")
    organization_type: OrganizationType = Field(..., description="Тип организации")
    organization_url: str | None = Field(default=None, description="URL сайта организации")
    description: str | None = Field(default=None, description="Описание деятельности организации")
    use_ai_consultant: bool = Field(
        default=True, description="Использовать ли AI консультанта для работы с workspace"
    )
