from dataclasses import dataclass

from .models import (
    DEFAULT_TEMPERATURE,
    CompletionOptions,
    ReasoningMode,
    ReasoningOptions,
    ToolChoiceMode,
)

BASE_URL = "https://llm.api.cloud.yandex.net"


@dataclass
class BaseFoundationModel:
    api_key: str
    iam_token: str
    folder_id: str
    model_name: str
    base_url: str = BASE_URL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int | None = None
    timeout: int = 30
    streaming: bool = False
    reasoning_mode: ReasoningMode = "REASONING_MODE_UNSPECIFIED"
    tool_choice_mode: ToolChoiceMode = "TOOL_CHOICE_MODE_UNSPECIFIED"

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.iam_token}"}

    @property
    def _model_uri(self) -> str:
        return f"gpt://{self.base_url}/{self.model_name}"

    @property
    def _completion_options(self) -> CompletionOptions:
        return CompletionOptions(
            stream=self.streaming,
            temperature=self.temperature,
            maxTokens=self.max_tokens,
            reasoningOptions=ReasoningOptions(mode=self.reasoning_mode),
        )
