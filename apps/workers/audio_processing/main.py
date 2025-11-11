from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from client import ClientV1
from config.dev import settings as dev_settings
from modules.orchestration.domain.commands import ProcessAudioCommand
from modules.orchestration.domain.events import ChunkPrecessedEvent

from .splitter import AudioSplitter

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = ClientV1(base_url=...)


def calculate_chunk_duration(collection_duration, record_count: int) -> int:
    ...


@broker.subscriber("audio_processing")
@broker.publisher("audio_processing")
async def handle_process_audio_command(command: ProcessAudioCommand, logger: Logger) -> ...:
    chunk_duration = calculate_chunk_duration(..., ...)
    splitter = AudioSplitter(
        chunk_duration=chunk_duration, chunk_format="wav", prefix=command.collection_id
    )
    async for chunk_content, chunk_duration in splitter.split_stream(...):
        ...
