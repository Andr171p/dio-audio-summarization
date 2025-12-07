import asyncio
from collections.abc import AsyncIterable, AsyncIterator
from uuid import UUID

import aiohttp

from modules.shared_kernel.application import UnitOfWork
from modules.shared_kernel.application.exceptions import NotFoundError

from ..domain import FileMetadata, FilePart, UploadFileCommand
from .queries import DownloadFileQuery
from .reposiotry import FileMetaRepository
from .storage import Storage


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


class MediaService:
    def __init__(
            self, uow: UnitOfWork, repository: FileMetaRepository, storage: Storage
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._storage = storage

    async def upload_file(
            self, command: UploadFileCommand, file_stream: AsyncIterable[bytes]
    ) -> FileMetadata:
        file_metadata = FileMetadata.create(command)
        async with self._uow.transactional() as uow:
            created_file_metadata = await self._repository.create(file_metadata)
            await self._storage.upload_multipart(file_metadata.generate_file_parts(file_stream))
            await uow.commit()
        return created_file_metadata

    async def get_file_metadata(self, file_id: UUID) -> FileMetadata:
        file_metadata = await self._repository.read(file_id)
        if file_metadata is None:
            raise NotFoundError(
                "File not found", entity_name="FileMetadata", details={"file_id": file_id}
            )
        return file_metadata

    async def download_file(self, query: DownloadFileQuery) -> AsyncIterator[FilePart]:
        file_metadata = self.get_file_metadata(query.file_id)
        async for file_part in self._storage.download_multipart(
            filepath=file_metadata.filepath, part_size=query.chunk_size
        ):
            yield file_part

    async def remove_file(self, file_id: UUID) -> None:
        async with self._uow as uow:
            file_metadata = await self.get_file_metadata(file_id)
            await self._storage.remove(file_metadata.filepath)
            await self._repository.delete(file_metadata.id)
            await uow.commit()
