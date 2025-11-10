from typing import Final

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings

broker: Final[RabbitBroker] = RabbitBroker(url=dev_settings.rabbitmq.url)

app: Final[FastStream] = FastStream(broker)
