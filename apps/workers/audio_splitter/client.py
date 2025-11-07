from collections.abc import AsyncIterable
from uuid import UUID

import aiohttp

from modules.shared_kernel.file_managment import FilePart

BASE_URL = "http://localhost:8000/api/v1"
CHUNK_SIZE = ...


async def get_collection(collection_id: ...) -> ...: ...


async def download_record(
        collection_id: UUID, record_id: UUID, chunk_size: int,
) -> AsyncIterable[bytes]:
    url = f"{BASE_URL}/collections/{collection_id}/records/{record_id}/download"
    params = {"chunk_size": chunk_size}
    try:
        async with aiohttp.ClientSession() as session, session.get(
                url=url, params=params, stream=True
        ) as response:
            response.raise_for_status()
            ...
    except aiohttp.ClientError:
        ...
