from typing import Protocol

from collections.abc import AsyncIterable

from ..file_managment import File, FilePart, Filepath


class Storage(Protocol):
    """Файловое/объектное хранилище"""

    async def upload(self, file: File) -> None: pass

    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None: pass

    async def download(self, filepath: Filepath) -> File | None: pass

    async def download_multipart(self, filepath: Filepath) -> AsyncIterable[FilePart]: pass

    async def remove(self, filepath: Filepath) -> bool: pass

    async def exists(self, filepath: Filepath) -> bool: pass
