from typing import Protocol

import asyncio
import logging

from .dto import Pagination
from .message_bus import AnyMessage
from .outbox import OutboxMessage, OutboxRepository, OutboxStatus
from .uow import UnitOfWork

logger = logging.getLogger(__name__)


class AnyHandler(Protocol):
    async def handle(self, message: AnyMessage) -> None: ...


class OutboxWorker:
    MIN_MESSAGES = 50

    def __init__(
            self,
            uow: UnitOfWork,
            repository: OutboxRepository,
            handlers: dict[str, AnyHandler],
            timeout: int = 30,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._handlers = handlers
        self._timeout = timeout

    async def start(self) -> None:
        while True:
            try:
                async with self._uow.transactional() as uow:
                    messages = await self._repository.get_by_status(
                        OutboxStatus.PENDING,
                        pagination=Pagination(page=1, limit=self.MIN_MESSAGES)
                    )
                    for message in messages:
                        await self._process_message(message)
                    await uow.commit()
                    if len(messages) < self.MIN_MESSAGES:
                        await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.exception("Error in outbox worker: {e}")
                await asyncio.sleep(self._timeout)

    async def _process_message(self, message: OutboxMessage) -> None:
        handler = self._handlers.get(message.message_type)
        if handler is None:
            error = f"No handler for message type {message.message_type}"
            logger.warning(error)
            message.mark_failed(error)
            await self._repository.update(message.id, **message.model_dump())
            return
        message.mark_processing()
        await self._repository.update(message.id, **message.model_dump())
        try:
            await handler.handle(message)
            message.mark_processed()
        except Exception as e:
            logger.exception("Error processing message %s: {e}", message.id)
            message.mark_failed(str(e))
        await self._repository.update(message.id, **message.model_dump())
