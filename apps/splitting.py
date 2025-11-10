import asyncio
import logging
import operator
import subprocess  # noqa: S404
from asyncio.subprocess import Process
from collections.abc import AsyncIterable, AsyncIterator

logger = logging.getLogger(__name__)


class AudioStreamSplitter:
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


async def main() -> None:
    import aiofiles  # noqa: PLC0415

    async def audio_stream_generator(filepath: str) -> AsyncIterator[bytes]:
        async with aiofiles.open(filepath, "rb") as file:
            chunk_size = 8192
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    file = "22 окт., 09.38_.mp3"
    splitter = AudioStreamSplitter(chunk_duration=60 * 20, output_format="wav")
    chunk_count = 0
    total_duration = 0
    async for chunk_data, duration in splitter.split_on_chunks(
            audio_stream_generator(file),
            samplerate=44100,
            bitrate=128000
    ):
        chunk_count += 1
        total_duration += duration
        print(  # noqa: T201
            f"Чанк {chunk_count}: размер={len(chunk_data)} байт, длительность={duration:.2f} сек"
        )


if __name__ == "__main__":
    asyncio.run(main())
