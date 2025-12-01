from uuid import UUID

from modules.shared_kernel.domain import Event

from .value_objects import MessageRole


class MessageSentEvent(Event):
    chat_id: UUID
    role: MessageRole
    text: str
