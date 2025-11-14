from typing import Protocol

import logging

from ..domain import CommandT, EventT

logger = logging.getLogger(__name__)

Message = CommandT | EventT


class MessageBus(Protocol):
    """Шина сообщений (интерфейс-адаптер для брокеров сообщений)"""

    async def publish(self, message: Message, **kwargs) -> None: pass


class LogMessageBus(MessageBus):
    async def publish(self, message: Message, **kwargs) -> None:  # noqa: PLR6301
        logger.info("Publish message %s", message.model_dump())
