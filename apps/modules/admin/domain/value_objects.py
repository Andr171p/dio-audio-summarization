from enum import StrEnum


class WorkspaceType(StrEnum):
    """Тип рабочего пространства"""

    PUBLIC = "public"
    PRIVATE = "private"


class OrganizationType(StrEnum):
    """Тип организации"""

    # Коммерческие организации
    CORPORATION = "corporation"
    SMALL_BUSINESS = "small_business"
    STARTUP = "startup"
    # Образовательные учреждения
    UNIVERSITY = "university"
    SCHOOL = "school"
    # Государственные структуры
    GOVERNMENT = "government"
    # Сфера услуг
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    CONSULTING = "consulting"
    RETAIL = "retail"
    # Креативные индустрии
    MEDIA = "media"
    ADVERTISING = "advertising"
    DESIGN = "design"
    # Другое
    OTHER = "other"
