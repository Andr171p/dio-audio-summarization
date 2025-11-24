from typing import Protocol

from abc import abstractmethod
from collections.abc import AsyncIterable

from ..files import File, FilePart, Filepath

EXPIRES_IN = 3600


class Storage(Protocol):
    """Файловое/объектное хранилище"""

    @abstractmethod
    async def upload(self, file: File) -> None: pass

    @abstractmethod
    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None: pass

    @abstractmethod
    async def download(self, filepath: Filepath) -> File | None: pass

    @abstractmethod
    async def download_multipart(
            self, filepath: Filepath, part_size: int
    ) -> AsyncIterable[FilePart]: pass

    @abstractmethod
    async def remove(self, filepath: Filepath) -> bool: pass

    @abstractmethod
    async def exists(self, filepath: Filepath) -> bool: pass

    async def generate_presigned_url(
            self, filepath: Filepath, expires_in: int = EXPIRES_IN
    ) -> str: pass
