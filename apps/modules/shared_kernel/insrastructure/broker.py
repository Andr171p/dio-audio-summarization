from typing import Final

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from config.dev import settings

broker: Final[RabbitBroker] = RabbitBroker(url=settings.rabbitmq.url)

app: Final[FastStream] = FastStream(broker)
