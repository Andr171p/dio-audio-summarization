from typing import Any, Self

from collections import UserList
from uuid import UUID

from pydantic import Field, PositiveInt, computed_field, model_validator

from modules.shared_kernel.domain import AggregateRoot, Entity

from .value_objects import MessageRole


class Message(Entity):
    """Сообщение внутри чата.

    Attributes:
        chat_id: Идентификатор чата.
        role: Роль отправителя.
        text: Текст сообщения.
        attachments: Медиа вложения, содержит список медиа идентификаторов (file_id).
        metadata: Дополнительные метаданные сообщения.
    """

    chat_id: UUID
    role: MessageRole
    text: str
    attachments: list[UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Conversation(UserList[Message]):
    """Текущий диалог ИИ с пользователем"""

    def to_markdown(self) -> str:
        """Приводит последовательность сообщений в Markdown формат"""

        if not self.data:
            return ""
        return "\n".join([
            f"({i}) [{message.role}]: {message.text}"
            for i, message in enumerate(self.data)
        ])


class Chat(AggregateRoot):
    user_id: UUID
    title: str
    messages_count: PositiveInt
    conversation: Conversation = Field(default_factory=list)

    @computed_field(description="Количество сообщений в текущем диалоге")
    def conversation_length(self) -> PositiveInt:
        return len(self.conversation)

    @model_validator(mode="after")
    def _validate_invariant(self) -> Self:
        ...

    @classmethod
    def create(cls, user_id: UUID, title: str) -> Self: ...

    def send_message(self, command: ...) -> ...: ...
