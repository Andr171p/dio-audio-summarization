import asyncio
import logging

from config.dev import settings
from salute_speech.asyncio import AsyncSaluteSpeechClient

logger = logging.getLogger(__name__)


async def transcribe_audio(
        audio: bytes, max_speakers_count: int = 10, async_timeout: int = 1, **kwargs
) -> str:
    """Асинхронная трансрибация аудио записи.

    :param audio: Байты аудио контента.
    :param max_speakers_count: Максимальное количество спикеров на записи.
    :param async_timeout: Время задержки между polling запросами.
    :returns: Трансрибация в формате Markdown.
    """

    stt_client = AsyncSaluteSpeechClient(
        apikey=settings.salute_speech.apikey, scope=settings.salute_speech.scope
    )
    request_file_id = await stt_client.upload_file(
        file=audio, audio_encoding="PCM_S16LE", **kwargs
    )
    task = await stt_client.async_recognize(
        request_file_id=request_file_id, audio_encoding=..., max_speakers_count=max_speakers_count
    )
    while task.status != "DONE":
        await asyncio.sleep(async_timeout)
        task = await stt_client.get_task_status(task.id)
    response_file_id = task.response_file_id
    recognized_speech_list = await stt_client.download_file(response_file_id)
    return recognized_speech_list.to_markdown()
