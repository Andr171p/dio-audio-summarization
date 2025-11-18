from typing import Final

from faststream import FastStream
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange

from config.dev import settings as dev_settings

from ...application import Message, MessageBus

broker: Final[RabbitBroker] = RabbitBroker(url=dev_settings.rabbitmq.url)

app: Final[FastStream] = FastStream(broker)

app_exchange: Final[RabbitExchange] = RabbitExchange(name="app_exchange", type=ExchangeType.FANOUT)


class RabbitMQMessageBus(MessageBus):
    def __init__(self, broker: RabbitBroker) -> None:
        self.broker = broker

    async def send(self, message: Message, **kwargs) -> None:
        await self.broker.publish(message, exchange=app_exchange, **kwargs)
