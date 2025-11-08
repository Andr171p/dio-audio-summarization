import logging
from collections.abc import AsyncIterable
from uuid import UUID

import aiohttp

from .schemas import Collection, Record

logger = logging.getLogger(__name__)


class CollectionsResource:
    def __init__(self, route_path: str) -> None:
        self._route_path = route_path

    async def create(self, user_id: UUID, topic: str) -> Collection:
        try:
            async with aiohttp.ClientSession() as session, session.post(
                url=self._route_path, json={"user_id": user_id, "topic": topic}
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Collection.model_validate(data)
        except aiohttp.ClientError:
            ...

    async def get(self, collection_id: UUID) -> Collection:
        try:
            async with aiohttp.ClientSession() as session, session.post(
                url=f"{self._route_path}/{collection_id}"
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Collection.model_validate(data)
        except aiohttp.ClientError:
            ...

    async def upload_record(
            self,
            collection_id: UUID,
            file: AsyncIterable[bytes],
            filename: str,
            filesize: float,
            duration: float,
            channels: int | None = None,
            samplerate: int | None = None,
            bitrate: int | None = None,
    ) -> Record:
        endpoint_url = f"{self._route_path}/{collection_id}/records/upload"
        headers: dict[str, str] = {
            "filename": filename, "filesize": str(filesize), "duration": str(duration)
        }
        if channels is not None:
            headers["channels"] = str(channels)
        if samplerate is not None:
            headers["samplerate"] = str(samplerate)
        if bitrate is not None:
            headers["bitrate"] = str(bitrate)
        try:
            async with aiohttp.ClientSession() as session, session.post(
                url=endpoint_url, headers=headers, data=file
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Record.model_validate(data)
        except aiohttp.ClientError:
            ...

    async def get_record(self, record_id: UUID) -> Record:
        try:
            async with aiohttp.ClientSession() as session, session.get(
                url=f"{self._route_path}/{record_id}"
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Record.model_validate(data)
        except aiohttp.ClientError:
            ...

    async def download_record(
            self, record_id: UUID, chunk_size: int = ...
    ) -> AsyncIterable[bytes]:
        endpoint_url = f"{self._route_path}/records/{record_id}/download"
        params = {"chunk_size": chunk_size}
        try:
            async with aiohttp.ClientSession() as session, session.get(
                url=endpoint_url, params=params
            ) as response:
                response.raise_for_status()
                async for chunk in response.content.iter_chunks(chunk_size):
                    yield chunk
        except aiohttp.ClientError:
            ...
