import asyncio

from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from config.dev import settings as dev_settings
from modules.shared_kernel.audio import AudioSegment
from modules.summarization.domain import AudioTranscribedEvent
from salute_speech.asyncio import AsyncSaluteSpeechClient

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

salute_speech_client = AsyncSaluteSpeechClient(
    apikey=dev_settings.salute_speech.apikey,
    scope=dev_settings.salute_speech.scope,
)


async def transcribe_audio(audio_segment: AudioSegment) -> str:
    request_file_id = await salute_speech_client.upload_file(
        file=audio_segment.content, audio_encoding="PCM_S16LE"
    )
    task = await salute_speech_client.async_recognize(
        request_file_id, channels=audio_segment.channels, max_speakers_count=10
    )
    while task.status != "DONE":
        await asyncio.sleep(1)
        task = await salute_speech_client.get_task_status(task.id)
    recognized_speech_list = await salute_speech_client.download_file(task.response_file_id)
    return recognized_speech_list.to_markdown()


@broker.subscriber("audio_transcribing")
@broker.publisher("audio_transcribing")
async def handle_audio_transcribing(
        audio_segment: AudioSegment, logger: Logger
) -> AudioTranscribedEvent:
    text = await transcribe_audio(audio_segment)
    logger.info(
        "Audio transcribing successfully for segment %s/%s",
        audio_segment.id, audio_segment.total_count
    )
    return AudioTranscribedEvent(
        collection_id=audio_segment.metadata["collection_id"],
        record_id=audio_segment.metadata["record_id"],
        segment_id=audio_segment.id,
        segment_duration=audio_segment.duration,
        segments_count=audio_segment.total_count,
        text=text,
    )
