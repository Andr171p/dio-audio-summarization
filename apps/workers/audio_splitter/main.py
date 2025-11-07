from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.orchestration.domain.entities import SplitAudioCommand

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)


@broker.subscriber("audio_splitting")
@broker.publisher("audio_conversion")
async def handle_audio_splitting(command: SplitAudioCommand, logger: Logger) -> ...:
    ...
