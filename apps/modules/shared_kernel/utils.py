import asyncio
from collections.abc import AsyncIterable
from datetime import datetime
from uuid import uuid4

import aiohttp

from config.base import APP_NAME, TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""
    return datetime.now(TIMEZONE)


def generate_correlation_id() -> str:
    """Генерация уникального correlation id (используется для трассировки взаимодействий
    между приложениями)
    """
    return f"{APP_NAME}--{round(current_datetime().timestamp(), 2)}--{uuid4()}"


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
