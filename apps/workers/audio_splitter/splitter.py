import asyncio
import subprocess  # noqa: S404
from collections.abc import AsyncIterable

CHUNK_SIZE = 8192


async def _consume_ffmpeg(stream: AsyncIterable[bytes]):
    """Обработка выходного потока сегментов"""
    async for chunk in stream:
        yield chunk


async def split_on_chunks(
        stream: AsyncIterable[bytes], chunk_duration: int = ...
) -> AsyncIterable[bytes]:
    ffmpeg_command = [
        "ffmpeg",
        "-i", "pipe:0",  # Ввод в stdin
        "-f", "segment",  # Формат вывода - сегменты
        "-segment_time", f"{chunk_duration}",
        "-c", "copy",  # Копирование без перекодирования (для быстроты)
        "-reset_timestamps", "1",  # Сброс таймстампа для каждого сегмента
        "-map", "0:a"  # Получение только аудио дорожки,
        "pipe:1"  # Вывод в stdout
    ]
    process = await asyncio.create_subprocess_exec(
        **ffmpeg_command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    try:
        async def feed_ffmpeg() -> None:
            async for chunk in stream:
                process.stdin.write(chunk)
            process.stdin.close()

        async def read_ffmpeg() -> AsyncIterable[bytes]:
            while True:
                chunk = await process.stdout.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

        await asyncio.gather(feed_ffmpeg(), _consume_ffmpeg(read_ffmpeg()))
    except ...:
        ...
    finally:
        if process.returncode is None:
            process.terminate()
            await process.wait()
