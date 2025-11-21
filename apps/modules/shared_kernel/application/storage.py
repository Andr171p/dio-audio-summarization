from typing import Protocol

from collections.abc import AsyncIterable

from ..files import File, FilePart, Filepath

EXPIRES_IN = 3600


class Storage(Protocol):
    """Файловое/объектное хранилище"""

    async def upload(self, file: File) -> None: pass

    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None: pass

    async def download(self, filepath: Filepath) -> File | None: pass

    async def download_multipart(
            self, filepath: Filepath, part_size: int
    ) -> AsyncIterable[FilePart]: pass

    async def remove(self, filepath: Filepath) -> bool: pass

    async def exists(self, filepath: Filepath) -> bool: pass

    async def generate_presigned_url(
            self, filepath: Filepath, expires_in: int = EXPIRES_IN
    ) -> str: pass
