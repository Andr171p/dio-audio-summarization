import logging
from abc import ABC, abstractmethod

from ..domain import CommandT, EventT

logger = logging.getLogger(__name__)

AnyMessage = CommandT | EventT


class MessageBus(ABC):
    """Шина сообщений (интерфейс-адаптер для брокеров сообщений)"""

    @abstractmethod
    async def send(self, message: AnyMessage, **kwargs) -> None: pass


class LogMessageBus(MessageBus):
    async def send(self, message: AnyMessage, **kwargs) -> None:  # noqa: ARG002, PLR6301
        logger.info("Publish message %s", message.model_dump())
