from typing import Any

import asyncio
import glob
import json
import logging
import os
import re
from collections.abc import AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

import aiofiles

from modules.shared_kernel.audio import AudioFormat, AudioSegment

logger = logging.getLogger(__name__)

Prefix = str | UUID | float  # Уникальный префикс


class AudioSplitter:
    """Разделение аудио на чанки по продолжительности + конвертация чанков в заданный формат.

    Схема работы:

    AsyncIterable[bytes] ──► 1. Запись во временный файл (temp_audio_file.input)
    2. ffmpeg разбиение по аудио фреймам ──► chunk_000.wav, chunk_001.wav, ...
    3. Чтение чанков + получение метаданных ──► yield AudioSegment
    """

    def __init__(
            self, chunk_duration: int, chunk_format: AudioFormat = "wav", prefix: Prefix = "",
    ) -> None:
        """
        :param chunk_duration: Продолжительность чанка в секундах.
        :param chunk_format: Формат чанка на выходе, например: 'wav', 'mp3', ...
        :param prefix: Уникальный префикс для избежания коллизий и конфликтов данных.
        """
        self._chunk_duration = chunk_duration
        self._chunk_format = chunk_format
        self._prefix = prefix

    @property
    def _ffmpeg_output_pattern(self) -> str:
        """Паттерн для выходных результатов FFmpeg"""
        return f"{self._prefix}_chunk_%03d.{self._chunk_format}"

    async def _write_input_file(
            self, stream: AsyncIterable[bytes], suffix: str | None = None
    ) -> Path:
        """Записывает входное аудио во временный файл.

        :param stream: Поток аудио байтов (для записи по частям).
        :param suffix: Расширение временного файла (*опционально)
        :returns: Путь до временного файла.
        """
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
    async def _probe_file_metadata(filepath: Path) -> dict[str, float]:
        """Получение метаданных аудио файла
        (длительность, частота дискретизации, количество каналов)
        """
        ffprobe_command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "a",  # Только аудио потоки
            f"{filepath}",
        ]
        logger.debug(
            "FFprobe executing command for probe metadata %s", " ".join(ffprobe_command)
        )
        process = await asyncio.create_subprocess_exec(
            *ffprobe_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            error_message = (
                f"FFprobe error while probe metadata of file {filepath}, "
                f"returned code {process.returncode}, "
                f"error message: {stderr.decode()}"
            )
            logger.error(error_message)
            raise RuntimeError(error_message)
        try:
            data = json.loads(stdout.decode())
            audio_stream = None
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "audio":
                    audio_stream = stream
                    break
            if audio_stream is None:
                return {}
            return {
                "duration": float(audio_stream.get("duration", 0)),
                "samplerate": float(audio_stream.get("sample_rate", 0)),
                "channels": float(audio_stream.get("channels", 0)),
            }
        except RuntimeError:
            logger.exception(
                "Error occurred while probe metadata of file %s, error message: {e}",
                filepath
            )
            return {}

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

    async def _iter_chunks(
            self, metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[AudioSegment]:
        if metadata is None:
            metadata = {}
        files = sorted(
            glob.glob(self._ffmpeg_output_pattern.replace("%03d", "*")),
            key=lambda x: int(
                re.search(rf"{self._prefix}_chunk_(\d+)\.{self._chunk_format}", x).group(1)
            )
        )
        total_count = len(files)
        for id, filepath in enumerate(files):  # noqa: A001
            file_metadata = await self._probe_file_metadata(Path(filepath))
            if not file_metadata:
                raise ValueError(f"Empty metadata for file {filepath}")
            async with aiofiles.open(filepath, mode="rb") as file:
                content = await file.read()
            yield AudioSegment(
                id=id + 1,
                total_count=total_count,
                content=content,
                duration=int(file_metadata["duration"]),
                format=AudioFormat.from_filepath(filepath),
                size=len(content),
                samplerate=int(file_metadata["samplerate"]),
                channels=int(file_metadata["channels"]),
                metadata=metadata.copy(),
            )
            try:
                os.unlink(filepath)
            except (PermissionError, OSError):
                logger.exception("Error occurred while unlinking file %s", filepath)

    async def split_stream(
            self, stream: AsyncIterable[bytes], metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[AudioSegment]:
        """Потоковое разделение аудио на чанки с переконвертацией.

        :param stream: Поток байтов аудио записи.
        :param metadata: Дополнительные данные, которые нужно передать в контекст чанков.
        :returns: Байты чанка + фактическая продолжительность чанка.
        """
        input_file = await self._write_input_file(stream)
        async with self._ffmpeg_pipe(input_file, self._ffmpeg_output_pattern) as process:
            _, stderr = await process.communicate()
            if process.returncode != 0:
                error_message = stderr.decode()
                logger.error("FFmpeg process failed with error: %s", error_message)
                raise RuntimeError(f"FFmpeg process failed with error: {error_message}")
            async for chunk in self._iter_chunks(metadata):
                yield chunk
            os.unlink(input_file)


async def stream_file(filepath: str) -> AsyncIterable[bytes]:
    async with aiofiles.open(filepath, mode="rb") as file:
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            yield chunk


async def main() -> None:
    stream = stream_file("22 окт., 09.38_.mp3")
    splitter = AudioSplitter(chunk_duration=20 * 60, prefix="1234567")
    async for chunk in splitter.split_stream(stream):
        print(chunk.model_dump(exclude={"content"}))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
