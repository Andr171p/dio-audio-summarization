from uuid import UUID

from modules.shared_kernel.domain import Command

from .value_objects import MessageRole


class SendMessageCommand(Command):
    """Отправка сообщения в чат"""

    chat_id: UUID
    role: MessageRole = MessageRole.USER
    text: str
    attachments: list[...]
