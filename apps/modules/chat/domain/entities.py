from typing import Any, Self

from datetime import datetime
from uuid import UUID

from pydantic import Field, PositiveInt, model_validator

from modules.shared_kernel.domain import AggregateRoot, Entity, InvariantViolationError

from .primitives import Filename, Filepath
from .value_objects import FileType, MessageRole


class Attachment(Entity):
    file_id: UUID
    filename: Filename
    format: str
    type: FileType
    size: PositiveInt
    metadata: dict[str, Any] = Field(default_factory=dict)


class Message(Entity):
    role: MessageRole
    text: str
    attachments: list[Attachment] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class File(Entity):
    path: Filepath
    size: PositiveInt
    content: bytes
    uploaded_at: datetime


class Chat(AggregateRoot):
    user_id: UUID
    title: str
    messages_count: PositiveInt
    conversation_length: PositiveInt
    conversation: list[Message] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_invariant(self) -> Self:
        if self.conversation_length != len(self.conversation):
            raise InvariantViolationError(
                "Conversation length does not match the number of messages",
                entity_name=self.__class__.__name__,
                details={
                    "chat_id": self.id,
                    "conversation_length": self.conversation_length,
                    "messages_length": len(self.conversation),
                }
            )
        return self

    @classmethod
    def create(cls, user_id: UUID, title: str) -> Self: ...

    def send_message(self, command: ...) -> ...: ...
