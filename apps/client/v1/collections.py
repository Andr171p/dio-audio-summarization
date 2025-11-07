import logging
from uuid import UUID

import aiohttp


async def create(user_id: UUID, topic: str) -> ...:
    payload = {"user_id": user_id, "topic": topic}
    try:
        async with aiohttp.ClientSession() as session, session.post(
            url=..., json=payload
        ) as response:
            response.raise_for_status()
            data = await response.json()
    except ...:
        ...
