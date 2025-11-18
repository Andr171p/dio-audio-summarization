import logging
from abc import ABC, abstractmethod

from ..domain import CommandT, EventT

logger = logging.getLogger(__name__)

Message = CommandT | EventT


class MessageBus(ABC):
    """Шина сообщений (интерфейс-адаптер для брокеров сообщений)"""

    @abstractmethod
    async def send(self, message: Message, **kwargs) -> None: pass


class LogMessageBus(MessageBus):
    async def send(self, message: Message, **kwargs) -> None:  # noqa: PLR6301
        logger.info("Publish message %s", message.model_dump())
