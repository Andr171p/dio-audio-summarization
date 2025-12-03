import asyncio
import logging
from collections.abc import AsyncIterable

import aiofiles

from modules.audio.infrastructure.ffmpeg import FFMpegAudioSplitter

logger = logging.getLogger(__name__)


async def stream_file(filepath: str) -> AsyncIterable[bytes]:
    async with aiofiles.open(filepath, mode="rb") as file:
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            yield chunk


async def main() -> None:
    stream = stream_file("22 окт., 09.38_.mp3")
    splitter = FFMpegAudioSplitter(
        segment_duration=20 * 60, segment_overlap=..., prefix="1234567"
    )
    async for chunk in splitter.split_stream(stream):
        print(chunk.model_dump(exclude={"content"}))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
