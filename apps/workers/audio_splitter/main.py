import asyncio
import logging
import subprocess  # noqa: S404
from collections.abc import AsyncIterable, AsyncIterator

from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from client import ClientV1
from config.dev import settings as dev_settings
from modules.orchestration.domain.commands import SplitAudioCommand

logger = logging.getLogger(__name__)

CHUNK_SIZE = 8192  # Оптимальный размер буфера для чтения и записи
BUFFER_SIZE = 8192

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = ClientV1(base_url=..., timeout=...)


async def split_on_chunks(  # noqa: C901, PLR0915
        file_stream: AsyncIterable[bytes],
        chunk_duration: float,
        input_format: str,
        output_format: str = "wav",
        samplerate: float | None = None,
        bitrate: float | None = None,
) -> AsyncIterator[bytes]:
    """Асинхронное разбиение и конвертация аудио потока на чанки с заданной продолжительностью.

    :param file_stream: Асинхронный итератор, возвращающий байты аудио-записи.
    :param chunk_duration: Продолжительность каждого чанка в секундах.
    :param input_format: Формат входной аудио записи.
    :param output_format: Формат чанков на выходе (по умолчанию wav).
    :param samplerate: Опциональная частота дискретизации выходного аудио в Гц.
    :param bitrate: Опциональный битрейт выходного аудио в битах в секунду.
    """
    ffmpeg_command = [
        "ffmpeg",
        "-i", "pipe:0",  # Чтение из stdin
        "-f", output_format,
        "-acodec", "copy",  # Перекодирование по необходимости
        "-segment_time", f"{chunk_duration}",
        "-reset_timestamps", "1",  # Сброс временных меток для каждого чанка
        "-f", "segment",
        "pipe:1"  # Вывод в stdout
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
            bufsize=CHUNK_SIZE,
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
                yield chunk  # Ожидание завершения передачи данных
            try:
                await feed_ffmpeg()
            except TimeoutError:
                logger.warning("Timeout waiting for feed_ffmpeg to complete")
            returned_code = await process.wait()
            if returned_code != 0:
                stderr_message = ""
                if process.stderr:
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


@broker.subscriber("audio_splitting")
@broker.publisher("audio_conversion")
async def handle_audio_splitting(command: SplitAudioCommand, logger: Logger) -> ...:
    ...
