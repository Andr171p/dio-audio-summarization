from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.shared_kernel.utils import download_from_presigned_url

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)
