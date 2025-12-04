from enum import StrEnum


class MessageRole(StrEnum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
