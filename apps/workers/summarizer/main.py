from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.summarization.domain import (
    SummarizeTranscriptionCommand,
    TranscriptionSummarizedEvent,
)

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)


@broker.subscriber("summarizing")
@broker.publisher("summarizing")
async def handle_summarize_transcription_command(
        command: SummarizeTranscriptionCommand, logger: Logger
) -> TranscriptionSummarizedEvent: ...
