from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.shared_kernel.audio import AudioSegment
from salute_speech.asyncio import AsyncSaluteSpeechClient

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = AsyncSaluteSpeechClient(...)


@broker.subscriber("audio_transcribing")
@broker.publisher("transcription_summarizing")
async def transcribe_audio(audio_segment: AudioSegment, logger: Logger) -> ...:
    ...
