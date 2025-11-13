from typing import Protocol

from ..domain import CommandT, EventT

Message = CommandT | EventT


class MessageBus(Protocol):
    """Шина сообщений (интерфейс-адаптер для брокеров сообщений)"""

    async def publish(self, message: Message, **kwargs) -> None: pass
