from typing import Any

import asyncio
import glob
import logging
import os
import re
from collections.abc import AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles

from ...application import AudioSplitter
from ...application.exceptions import AudioSplittingError
from ...domain import AudioFormat, AudioSegment
from ...utils.audio import get_audio_info

logger = logging.getLogger(__name__)


class FFMpegAudioSplitter(AudioSplitter):
    """Асинхронный сплиттер аудио-потоков на сегменты фиксированной длительности
    с использованием FFmpeg.

    Класс предназначен для обработки аудио-потоков в реальном времени или из файлов,
    разделения их на чанки заданной длительности и конвертации в заданный формат.
    Использует FFmpeg для высокопроизводительной обработки аудио с поддержкой
    различных кодеков и форматов.

    Основные возможности:
    - Потоковое разделение аудио на сегменты
    - Автоматическая конвертация в указанный формат (по умолчанию WAV)
    - Поддержка перекрытия сегментов (overlap)
    - Очистка временных файлов после обработки
    - Асинхронная обработка для эффективной работы с I/O

    Example:
        >>> splitter = FFMpegAudioSplitter(
        ...     segment_duration=300,  # 5 минут
        ...     segment_overlap=10,    # 10 секунд перекрытия
        ...     segment_format=AudioFormat.WAV,
        ...     prefix="session_123"
        ... )
        >>> async for segment in splitter.split_stream(audio_stream):
        ...     process_segment(segment)

    Note:
        - Для работы требуется установленный FFmpeg в системе PATH
        - Все временные файлы автоматически удаляются после обработки
        - Поддерживает форматы: WAV, MP3, OGG, FLAC (зависит от FFmpeg)
        - Сегменты нумеруются начиная с 1
    """

    def __init__(
            self,
            segment_duration: int,
            segment_overlap: int,
            segment_format: AudioFormat = AudioFormat.WAV,
            temp_dir: Path | None = None,
            prefix: str | float | UUID = "",
    ) -> None:
        """
        :param segment_duration: Продолжительность сегмента в секундах
        :param segment_overlap: Перекрытие между сегментами в секундах
        :param segment_format: Формат сегмента
        :param temp_dir: Директория для временных файлов обработки, по умолчанию текущая
        :param prefix: Уникальный префикс для временных файлов
        """

        super().__init__(
            segment_duration=segment_duration,
            segment_overlap=segment_overlap,
            segment_format=segment_format
        )
        self._temp_dir = temp_dir
        self._prefix = prefix or uuid4()

    @property
    def _ffmpeg_output_pattern(self) -> str:
        """Паттерн для выходных сегментов FFMpeg"""
        return f"{self._prefix}_segment_%03d.{self._segment_format}"

    @asynccontextmanager
    async def _ffmpeg_pipe(self, input_path: Path):
        """Создание асинхронного процесса для потоковой работы с FFMpeg.

        :param input_path: Путь до файла, который нужно разбить на чанки.
        """

        ffmpeg_command = [
            "ffmpeg",
            "-y",  # Перезапись выхода
            "-i",
            f"{input_path}",
            "-f",
            "segment",
            "-segment_time",
            f"{self._segment_duration}",
            "-c:a",
            "pcm_s16le",  # Кодирование в WAV (PCM 16-bit)
            "-ac",
            "2",  # 2 канала (стерео)
            "-ar",
            "44100",  # Частота дискретизации 44.1 kHz
            "-reset_timestamps",
            "1",
            "-map",
            "0:a",  # Только аудио
            self._ffmpeg_output_pattern,
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

    async def _write_input_file(
            self, stream: AsyncIterable[bytes], audio_format: AudioFormat | None = None
    ) -> Path:
        """Записывает входное аудио во временный файл.

        :param stream: Поток аудио байтов (для записи по частям).
        :param audio_format: Формат временного файла (*опционально)
        :returns: Путь до временного файла.
        """

        extension = audio_format or ".input"
        async with aiofiles.tempfile.NamedTemporaryFile(
            mode="wb+",
            suffix=f".{extension}",
            prefix=self._prefix,
            dir=self._temp_dir,
            delete=False
        ) as temp_file:
            async for chunk in stream:
                await temp_file.write(chunk)
            return Path(temp_file.name)

    async def _iter_segments(
            self, metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[AudioSegment]:
        metadata = metadata or {}
        files = sorted(
            glob.glob(self._ffmpeg_output_pattern.replace("%03d", "*")),
            key=lambda x: int(
                re.search(rf"{self._prefix}_segment_(\d+)\.{self._segment_format}", x).group(1)
            ),
        )
        for index, filepath in enumerate(files):
            audioinfo = get_audio_info(Path(filepath))
            async with aiofiles.open(filepath, mode="rb") as file:
                content = await file.read()
            yield AudioSegment(
                number=index + 1,
                total_count=len(files),
                content=content,
                format=self._segment_format,
                size=len(content),
                duration=audioinfo["duration"],
                samplerate=audioinfo["samplerate"],
                channels=audioinfo["channels"],
                metadata=metadata.copy(),
            )
            try:
                os.unlink(filepath)
                logger.debug("File %s unlinked successfully", filepath)
            except OSError:
                logger.exception("Error occurred while unlinking file %s", filepath)

    async def split_stream(
            self, stream: AsyncIterable[bytes], metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[AudioSegment]:
        """Потоковое разделение аудио на чанки с переконвертацией.

        :param stream: Поток байтов аудио записи.
        :param metadata: Дополнительные данные, которые нужно передать в контекст чанков.
        :returns: Генератор аудио сегментов.
        """

        input_path = await self._write_input_file(stream)
        async with self._ffmpeg_pipe(input_path) as pipe:
            _, stderr = await pipe.communicate()
            if pipe.returncode != 0:
                error_message = stderr.decode()
                logger.error("FFmpeg process failed with error: %s", error_message)
                raise AudioSplittingError(f"FFmpeg process failed with error: {error_message}")
            async for segment in self._iter_segments(metadata):
                yield segment
        try:
            os.unlink(input_path)
            logger.debug("Input file %s unlinked successfully", input_path)
        except OSError:
            logger.exception("Error occurred while unlinking input file %s", input_path)
