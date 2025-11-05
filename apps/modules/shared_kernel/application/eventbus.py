from typing import Protocol

from ..domain import EventT


class EventBus(Protocol):
    """Шина событий (интерфейс-адаптер для брокеров сообщений)"""

    async def publish(self, event: EventT, **kwargs) -> None: pass


class PrintEventBus(EventBus):
    async def publish(self, event: EventT, **kwargs) -> None:  # noqa: PLR6301
        print(event.model_dump())  # noqa: T201
