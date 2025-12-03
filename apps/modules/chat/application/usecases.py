from ..domain import Chat, Message
from .repository import ChatRepository


class SendMessageUseCase:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self._chat_repository = chat_repository

    async def execute(self, message: Message) -> ...:
        ...
