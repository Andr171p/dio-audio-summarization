from abc import abstractmethod
from uuid import UUID

from modules.shared_kernel.application import CRUDRepository

from ..domain import Chat, Message


class ChatRepository(CRUDRepository[Chat]):
    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Chat]: ...

    @abstractmethod
    async def add_messages(self, messages: list[Message]) -> None: ...
