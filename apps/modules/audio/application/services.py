from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.media.application import FileMetaRepository, Storage
    from modules.media.domain import Filepath

import asyncio
import logging
import os
from pathlib import Path

import aiofiles

from config.dev import settings
from modules.shared_kernel.application.exceptions import NotFoundError
from salute_speech.asyncio import AsyncSaluteSpeechClient

from ..domain.entities import Audio
from ..utils.audio import extract_audio_info

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


class AudioMetaExtractor:
    def __init__(
            self,
            file_meta_repository: "FileMetaRepository",
            storage: "Storage",
            temp_dir: Path
    ) -> None:
        self._file_meta_repository = file_meta_repository
        self._storage = storage
        self._temp_dir = temp_dir

    async def extract(self, filepath: Filepath, part_size: int) -> Audio:
        filemeta = await self._file_meta_repository.get_by_filepath(filepath)
        if filemeta is None:
            raise NotFoundError(f"File {filepath} not found!", entity_name="FileMetadata")
        try:
            logger.info("Start scan file %s", filepath)
            async with aiofiles.tempfile.NamedTemporaryFile(
                mode="w",
                suffix=f".{filemeta.extension}",
                prefix="audio_scanning",
                dir=self._temp_dir,
                delete=False,
            ) as temp_file:
                async for file_part in self._storage.download_multipart(
                        filemeta.filepath, part_size=part_size
                ):
                    await temp_file.write(file_part.content)
                audioinfo = extract_audio_info(Path(temp_file.name))
            return Audio(
                file_id=filemeta.id,
                format=filemeta.extension,
                duration=audioinfo["duration"],
                channels=audioinfo["channels"],
                sample_rate=audioinfo["samplerate"],
                metadata={"filepath": filemeta.filepath},
            )
        except OSError:
            logger.exception(
                "Error occurred while extract audio metadata of file %s, error message: {e}",
                filepath
            )
        finally:
            os.unlink(temp_file.name)
            logger.info("Temp file %s deleted", filepath)
