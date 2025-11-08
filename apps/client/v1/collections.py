import logging
from uuid import UUID

import aiohttp

from .schemas import Collection, Record

logger = logging.getLogger(__name__)


async def create(user_id: UUID, topic: str) -> Collection:
    payload = {"user_id": user_id, "topic": topic}
    try:
        async with aiohttp.ClientSession() as session, session.post(
            url=..., json=payload
        ) as response:
            response.raise_for_status()
            data = await response.json()
        return Collection.model_validate(data)
    except ...:
        ...


async def get(collection_id: UUID) -> Collection:
    try:
        async with aiohttp.ClientSession() as session, session.post(
            url=..., params={"collection_id": collection_id}
        ) as response:
            response.raise_for_status()
            data = await response.json()
        return Collection.model_validate(data)
    except ...:
        ...


async def upload_record() -> Record: ...


async def get_record(record_id: UUID) -> Record: ...


async def download_record(record_id: UUID) -> ...: ...
