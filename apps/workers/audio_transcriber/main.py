from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.shared_kernel.audio import AudioSegment
from salute_speech.asyncio import AsyncSaluteSpeechClient

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

salute_speech_client = AsyncSaluteSpeechClient(
    apikey=dev_settings.salute_speech.apikey,
    scope=dev_settings.salute_speech.scope,
)


async def recognize_speech(audio_segment: AudioSegment) -> ...:
    request_file_id = await salute_speech_client.upload_file(
        file=audio_segment.content, audio_encoding=...
    )
    task = await salute_speech_client.async_recognize(
        request_file_id, channels=audio_segment.channels, max_speakers_count=10
    )


@broker.subscriber("audio_transcribing")
@broker.publisher("transcription_summarizing")
async def transcribe_audio(audio_segment: AudioSegment, logger: Logger) -> ...:
    ...
