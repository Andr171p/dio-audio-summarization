from enum import StrEnum

from pydantic import HttpUrl

from modules.shared_kernel.domain import ValueObject


class LLMProvider(StrEnum):
    OPENAI = "openai"
    GIGACHAT = "gigachat"
    YANDEX_FOUNDATION_MODELS = "yandex-foundation-models"
    OLLAMA = "ollama"


class ModelConfiguration(ValueObject):
    provider: LLMProvider
    model_name: str
    base_url: HttpUrl | None = None
    temperature: float | None = None
    top_p: float | None = None
