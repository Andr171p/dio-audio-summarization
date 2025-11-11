import asyncio
import glob
import logging
import os
import re
from collections.abc import AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

import aiofiles

logger = logging.getLogger(__name__)


class AudioSplitter:
    """Разделяет аудио на чанки с заданной размерностью + конвертирует чанки в нужный формат.

    Схема работы:

    AsyncIterable[bytes] ──► 1. Запись во временный файл (temp_example.input)
                         │
                         ▼
               2. ffmpeg (segment) → chunk_000.wav, chunk_001.wav …
                         │
                         ▼
               3. Чтение .wav‑чанков → yield (bytes, duration)
    """

    def __init__(
            self,
            chunk_duration: int,
            chunk_format: str = "wav",
            prefix: str | UUID | float = "",
    ) -> None:
        """
        :param chunk_duration: Продолжительность чанка в секундах.
        :param chunk_format: Формат чанка на выходе, например: 'wav', 'mp3', ...
        :param prefix: Уникальный префикс для избежания коллизий и конфликтов данных.
        (Строго рекомендуется к заполнению, пример: uuid, timestamp, hash, ...)
        """
        self._chunk_duration = chunk_duration
        self._chunk_format = chunk_format
        self._prefix = prefix
        self._ffmpeg_output_pattern = f"{self._prefix}_chunk_%03d.{self._chunk_format}"

    async def _write_file(self, stream: AsyncIterable[bytes], suffix: str | None = None) -> Path:
        suffix = suffix or ".input"
        async with aiofiles.tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix=self._prefix,
        ) as temp_file:
            async for chunk in stream:
                await temp_file.write(chunk)
            return Path(temp_file.name)

    @staticmethod
    async def _probe_duration(filepath: Path) -> float:
        """Получение длительности аудио файла"""
        ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            f"{filepath}",
        ]
        process = await asyncio.create_subprocess_exec(
            *ffprobe_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            try:
                return float(stdout.decode().strip())
            except RuntimeError:
                return 0.0
        else:
            logger.error("FFprobe error: %s", stderr.decode())
            return 0.0

    @asynccontextmanager
    async def _ffmpeg_pipe(self, input_file: Path, output_pattern: str):
        ffmpeg_command = [
            "ffmpeg",
            "-y",  # Перезапись выхода
            "-i", f"{input_file}",
            "-f", "segment",
            "-segment_time", f"{self._chunk_duration}",
            "-c:a", "pcm_s16le",  # Кодирование в WAV (PCM 16-bit)
            "-ac", "2",  # 2 канала (стерео)
            "-ar", "44100",  # Частота дискретизации 44.1 kHz
            "-reset_timestamps", "1",
            "-map", "0:a",  # Только аудио
            output_pattern
        ]
        logger.info("FFmpeg launch command: %s", " ".join(ffmpeg_command))
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        try:
            yield process
        finally:
            if process.returncode is None:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5)
                except TimeoutError:
                    process.kill()
                    await process.wait()

    async def _read_chunks(self) -> AsyncIterator[tuple[bytes, int]]:
        files = sorted(
            glob.glob(self._ffmpeg_output_pattern.replace("%03d", "*")),
            key=lambda x: int(re.search(r"_(\d+)\.wav$", x).group(1))
        )
        for filepath in files:
            duration = await self._probe_duration(Path(filepath))
            async with aiofiles.open(filepath, mode="rb") as file:
                content = await file.read()
            yield content, duration
            try:
                os.unlink(filepath)
            except (PermissionError, OSError):
                logger.exception("Error occurred while unlinking file %s", filepath)

    async def split_stream(
            self, stream: AsyncIterable[bytes]
    ) -> AsyncIterator[tuple[bytes, float]]:
        """Потоковое разделение аудио на чанки с переконвертацией.

        :param stream: Поток байтов аудио записи.
        :returns: Байты чанка + фактическая продолжительность чанка.
        """
        input_file = await self._write_file(stream)
        async with self._ffmpeg_pipe(input_file, self._ffmpeg_output_pattern) as process:
            _, stderr = await process.communicate()
            if process.returncode != 0:
                error_message = stderr.decode()
                logger.error("FFmpeg process failed with error: %s", error_message)
                raise RuntimeError(f"FFmpeg process failed with error: {error_message}")
            async for chunk_content, chunk_duration in self._read_chunks():
                yield chunk_content, chunk_duration
            os.unlink(input_file)
