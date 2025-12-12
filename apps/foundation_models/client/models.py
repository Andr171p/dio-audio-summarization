from typing import Any, Literal

from pydantic import BaseModel, Field, NonNegativeFloat, PositiveInt, field_validator

DEFAULT_TEMPERATURE = 0.3
ReasoningMode = Literal[
    "REASONING_MODE_UNSPECIFIED",
    "DISABLED",
    "ENABLED_HIDDEN"
]
ToolChoiceMode = Literal[
    "TOOL_CHOICE_MODE_UNSPECIFIED",
    "NONE",
    "AUTO",
    "REQUIRED"
]


class FunctionCall(BaseModel):
    """Вызов функции"""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """Вызов инструмента"""

    function_call: FunctionCall = Field(alias="functionCall")


class ToolCallList(BaseModel):
    """Представление списка вызываемых инструментов"""

    tool_calls: list[ToolCall] = Field(default_factory=list, alias="toolCalls")


class FunctionResult(BaseModel):
    """Результат выполнения функции"""

    name: str
    content: str


class ToolResult(BaseModel):
    """Результат вызова инструмента"""

    function_result: FunctionResult = Field(alias="functionResult")


class ToolResultList(BaseModel):
    """Список результатов вызванных инструментов"""

    tool_results: list[ToolResult] = Field(default_factory=list, alias="toolResults")


class Message(BaseModel):
    """Сообщение представляющее собой оболочку между входными и выходными данными LLM.
    Подробнее на https://yandex.cloud/ru/docs/ai-studio/text-generation/api-ref/TextGeneration/completion#yandex.cloud.ai.foundation_models.v1.Message
    """

    role: Literal["system", "assistant", "user"]
    text: str | None = None
    tool_call_list: ToolCallList | None = Field(default=None, alias="toolCallList")
    tool_result_list: ToolResultList | None = Field(default=None, alias="toolResultList")


class FunctionTool(BaseModel):
    """Функция как инструмент модели"""

    name: str
    description: str | None = None
    parameters: dict[str, Any] | None = None
    strict: bool | None = None


class Tool(BaseModel):
    """Инструмент"""

    function: FunctionTool


class JsonSchema(BaseModel):
    """JSON схема ответа"""

    schema_: dict[str, Any] = Field(alias="schema")


class ToolChoice(BaseModel):
    """Настройка выбора инструментов"""

    mode: ToolChoiceMode = "TOOL_CHOICE_MODE_UNSPECIFIED"
    function_name: str | None = Field(default=None, alias="functionName")


class ReasoningOptions(BaseModel):
    """Настройки рассуждения модели"""

    mode: ReasoningMode = "REASONING_MODE_UNSPECIFIED"


class CompletionOptions(BaseModel):
    """Опции генерации модели"""

    stream: bool = False
    temperature: NonNegativeFloat = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=1.0)
    max_tokens: PositiveInt | None = Field(default=None, alias="maxTokens")
    reasoning_options: ReasoningOptions = Field(alias="reasoningOptions")

    @field_validator("max_tokens", mode="after")
    def convert_max_tokens_to_str(cls, value: PositiveInt) -> str:
        return str(value)


class CompletionRequest(BaseModel):
    """Тело запроса для получения ответа от модели"""

    model_uri: str = Field(alias="modelUri")
    completion_options: CompletionOptions = Field(alias="completionOptions")
    messages: list[Message]
    tools: list[Tool] | None = None
    json_object: bool | None = Field(None, alias="jsonObject")
    json_schema: JsonSchema | None = Field(None, alias="jsonSchema")
    parallel_tool_calls: bool | None = Field(None, alias="parallelToolCalls")
    tool_choice: ToolChoice | None = Field(None, alias="toolChoice")


msg = Message(
    role="system",
    text="",
    toolCallList=ToolCallList(
        toolCalls=[ToolCall(
            functionCall=FunctionCall(name="multiply", arguments={"a": 1, "b": 2}))
        ]
    ),
)
