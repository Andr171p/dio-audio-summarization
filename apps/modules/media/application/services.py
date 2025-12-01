import asyncio
from collections.abc import AsyncIterable

import aiohttp


async def download_from_presigned_url(presigned_url: str, chunk_size: int) -> AsyncIterable[bytes]:
    """Скачивание файла используя пред-подписанный URL.
    Обеспечивает безопасное и доверенное скачивание.

    :param presigned_url: Пред-подписанный S3 URL для скачивания.
    :param chunk_size: Размер чанка в байтах для скачивания.
    """
    async with aiohttp.ClientSession() as session, session.get(presigned_url) as response:
        response.raise_for_status()
        async for chunk in response.content.iter_chunked(chunk_size):
            yield chunk
            await asyncio.sleep(0)
