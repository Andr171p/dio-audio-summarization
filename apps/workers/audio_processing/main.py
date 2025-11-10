import asyncio
import logging
import operator
import subprocess  # noqa: S404
from asyncio.subprocess import Process
from collections.abc import AsyncIterable, AsyncIterator

from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker
from tinytag import TinyTag

from client import ClientV1
from config.dev import settings as dev_settings
from modules.orchestration.domain.commands import ProcessAudioCommand
from modules.orchestration.domain.events import ChunkPrecessedEvent

logger = logging.getLogger(__name__)

CHUNK_SIZE = 8192  # Оптимальный размер буфера для чтения и записи
BUFFER_SIZE = 8192

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = ClientV1(base_url=..., timeout=...)


class AudioSplitter:
    def __init__(self, chunk_duration: float, output_format: str = "wav") -> None:
        self.chunk_duration = chunk_duration
        self.output_format = output_format

    def _build_ffmpeg_command(
            self, samplerate: int | None = None, bitrate: int | None = None
    ) -> list[str]:
        ffmpeg_command = [
            "ffmpeg",
            "-i", "pipe:0",  # Чтение из stdin
            "-f", self.output_format,
            "-acodec", "pcm_s16le" if self.output_format == "wav" else "copy",
            # Перекодирование по необходимости (PCM кодировка для WAV)
            "-segment_time", f"{self.chunk_duration}",
            "-reset_timestamps", "1",  # Сброс временных меток для каждого чанка
            "-f", "segment",
            "-segment_format", self.output_format,
            "-segment_list", "pipe:1",  # Метаданные в stdout
            "-segment_list_type", "flat",
            "pipe:2"  # Аудио-данные в stderr
        ]
        # Добавление опциональных параметров
        if samplerate is not None:
            ffmpeg_command.extend(["-ar", f"{samplerate}"])
        if bitrate is not None:
            ffmpeg_command.extend(["-b:a", f"{bitrate}"])
        return ffmpeg_command

    async def split_on_chunks(
            self,
            audio_stream: AsyncIterable[bytes],
            samplerate: int | None = None,
            bitrate: int | None = None,
    ) -> AsyncIterator[tuple[bytes, float]]:
        ffmpeg_command = self._build_ffmpeg_command(samplerate, bitrate)
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            limit=1024 * 1024 * 8,  # 8MB буфер
        )
        try:
            feed_audio_task = asyncio.create_task(self._feed_audio(process, audio_stream))
            read_chunks_metadata_task = asyncio.create_task(self._read_chunks_metadata(process))
            read_audio_chunks_task = asyncio.create_task(self._read_audio_chunks(process))
            async for chunk, chunk_duration in self._compare_chunks(
                read_chunks_metadata_task, read_audio_chunks_task
            ):
                yield chunk, chunk_duration
            await feed_audio_task
            await process.wait()
        except asyncio.CancelledError:
            logger.exception("Error occurred while splitting audio, error: {e}")
        finally:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except TimeoutError:
                process.kill()
                await process.wait()

    @staticmethod
    async def _feed_audio(process: Process, stream: AsyncIterable[bytes]) -> None:
        """Потоковая передача аудио"""
        try:
            async for chunk in stream:
                if process.stdin:
                    process.stdin.write(chunk)
                    # Нет ожидания drain для каждого чанка - системная буферизация
            if process.stdin:
                process.stdin.close()
        except BrokenPipeError:
            logger.exception("Error occurred while feed audio, error: {e}")

    async def _read_chunks_metadata(self, process: Process) -> list[tuple[int, float]]:
        """Чтение мета-данных чанков из stdout"""
        metadata: list[tuple[int, float]] = []
        if process.stdout:
            content = await process.stdout.read()
            # Парсим flat format: file1 duration1 file2 duration2...
            parts = content.decode().strip().split()
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    chunk_number = int(
                        parts[i]
                        .replace("chunk_", "")
                        .replace(f".{self.output_format}")
                    )
                    chunk_duration = float(parts[i + 1])
                    metadata.append((chunk_number, chunk_duration))
        return sorted(metadata, key=operator.itemgetter(0))

    @staticmethod
    async def _read_audio_chunks(process: Process) -> dict[int, bytes]:
        """Чтение аудио-данных из stderr с идентификацией чанков"""
        chunks: dict[int, bytes] = {}
        if process.stderr:
            content = await process.stderr.read()
            current_chunk = 1
            # Поиск RIFF заголовков для WAV
            riff_markers = []
            pos = 0
            while pos < len(content):
                marker_pos = content.find(b"RIFF", pos)
                if marker_pos == -1:
                    break
                riff_markers.append(marker_pos)
                pos = marker_pos + 4
            for i, start_pos in enumerate(riff_markers):
                end_pos = riff_markers[i + 1] if i + 1 < len(riff_markers) else len(content)
                chunks[current_chunk] = content[start_pos:end_pos]
                current_chunk += 1
        return chunks

    @staticmethod
    async def _compare_chunks(
            read_chunks_metadata_task: asyncio.Task, read_audio_chunks_task: asyncio.Task
    ) -> AsyncIterator[tuple[bytes, float]]:
        """Сопоставление мета-данных и аудио-данных чанков"""
        metadata = await read_chunks_metadata_task
        chunks = await read_audio_chunks_task
        for chunk_number, chunk_duration in metadata:
            if chunk_number in chunks:
                yield chunks[chunk_number], chunk_duration


async def split_on_chunks(  # noqa: C901, PLR0915
        file_stream: AsyncIterable[bytes],
        chunk_duration: float,
        samplerate: float | None = None,
        bitrate: float | None = None,
        output_format: str = "wav",
) -> AsyncIterator[tuple[bytes, float]]:
    """Асинхронное разбиение и конвертация аудио потока на чанки с заданной продолжительностью.

    :param file_stream: Асинхронный итератор, возвращающий байты аудио-записи.
    :param chunk_duration: Продолжительность каждого чанка в секундах.
    :param output_format: Формат чанков на выходе (по умолчанию wav).
    :param samplerate: Опциональная частота дискретизации выходного аудио в Гц.
    :param bitrate: Опциональный битрейт выходного аудио в битах в секунду.
    :returns Аудио байты чанка + фактическая длительность чанка.
    """
    ffmpeg_command = [
        "ffmpeg",
        "-i", "pipe:0",  # Чтение из stdin
        "-f", output_format,
        "-acodec", "pcm_s16le" if output_format == "wav" else "copy",
        # Перекодирование по необходимости (PCM кодировка для WAV)
        "-segment_time", f"{chunk_duration}",
        "-reset_timestamps", "1",  # Сброс временных меток для каждого чанка
        "-f", "segment",
        "-segment_format", output_format,
        "-segment_list", "pipe:1",  # Метаданные в stdout
        "-segment_list_type", "flat",
        "pipe:2"  # Аудио-данные в stderr
    ]
    # Добавление опциональных параметров
    if samplerate is not None:
        ffmpeg_command.extend(["-ar", f"{samplerate}"])
    if bitrate is not None:
        ffmpeg_command.extend(["-b:a", f"{bitrate}"])
    try:
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            limit=1024 * 1024 * 8,  # 8MB буфер
        )

        async def feed_ffmpeg() -> None:
            """Асинхронная передача данных из file_stream в stdin ffmpeg процесса"""
            try:
                async for chunk in file_stream:
                    if process.stdin is None:
                        raise RuntimeError("FFmpeg stdin is closed unexpectedly!")
                    process.stdin.write(chunk)
                    await process.stdin.drain()  # Ожидание записи данных
                if process.stdin:
                    process.stdin.close()
                    await process.stdin.wait_closed()
            except BrokenPipeError:
                logger.warning("FFmpeg process ended prematurely while feeding data!")

        async def consume_ffmpeg() -> AsyncIterator[bytes]:
            """Асинхронное чтение выходных данных из stdout ffmpeg процесса"""
            if process.stdout is None:
                raise RuntimeError("FFmpeg stdout is not available!")
            try:
                while True:
                    chunk = await process.stdout.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk
            except RuntimeError:
                logger.exception("Runtime error in consume_ffmpeg: {e}")
                raise

        feed_task = asyncio.create_task(feed_ffmpeg())
        try:
            async for chunk in consume_ffmpeg():
                tag = TinyTag.get(chunk)  # Получение продолжительности в секундах через TinyTag
                yield chunk, tag.duration  # Ожидание завершения передачи данных
            try:
                await feed_ffmpeg()
            except TimeoutError:
                logger.warning("Timeout waiting for feed_ffmpeg to complete")
            returned_code = await process.wait()
            if returned_code != 0 and process.stderr:
                stderr_message = await process.stderr.read()
                stderr_message = stderr_message.decode("utf-8", errors="ignore")
                logger.error(
                    "FFmpeg process finished with exit code %s, error: %s",
                    returned_code, stderr_message,
                )
                raise subprocess.CalledProcessError(
                    returned_code, ffmpeg_command, stderr=stderr_message
                )
        except asyncio.CancelledError:
            feed_task.cancel()
    except BrokenPipeError:
        logger.exception("Broken pipe error in split_on_chunks")


@broker.subscriber("audio_processing")
@broker.publisher("audio_processing")
async def handle_audio_processing(
        command: ProcessAudioCommand, logger: Logger
) -> ChunkPrecessedEvent:
    collection = await client.collections.get(command.collection_id)
    chunk_number = 1
    splitter = AudioSplitter(chunk_duration=command.chunk_duration, output_format="wav")
    for record in collection.records:
        logger.info(
            "Start processing audio record %s in '%s' collection", record.id, collection.topic
        )
        record_stream = client.collections.download_record(record.id, chunk_size=CHUNK_SIZE)
        chunks = splitter.split_on_chunks(
            record_stream,
            chunk_duration=command.chunk_duration,
            output_format="wav",
            samplerate=record.metadata.samplerate,
            bitrate=record.metadata.bitrate,
        )
        logger.info("Chunks splitting successfully for '%s' collection", collection.topic)
        async for content, duration in chunks:
            logger.info("Received %s chunk with %s duration", chunk_number, duration)
            yield ChunkPrecessedEvent(
                collection_id=collection.id,
                record_id=record.id,
                audio_format="wav",
                samplerate=record.metadata.samplerate,
                chunk_content=content,
                chunk_number=chunk_number,
                chunk_duration=duration,
                chunk_size=len(content),
            )
            chunk_number += 1
    logger.info("Finished processing audio records")
