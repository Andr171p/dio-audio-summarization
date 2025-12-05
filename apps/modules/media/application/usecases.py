from collections.abc import AsyncIterable
from uuid import UUID

from ..domain import FileMetadata
from ..domain.commands import UploadFileCommand
from .reposiotry import FileMetaRepository
from .storage import Storage


class UploadFileUsecase:
    def __init__(self, repository: FileMetaRepository, storage: Storage) -> None:
        self._repository = repository
        self._storage = storage

    async def execute(self, command: UploadFileCommand, file_stream: AsyncIterable[bytes]) -> UUID:
        file_metadata = FileMetadata.create(
            filename=command.filename,
            mime_type=command.mime_type,
            filesize=command.filesize,
            tenant=command.tenant,
            entity_type=command.entity_type,
            entity_id=command.entity_id,
        )
        await self._repository.create(file_metadata)
        await self._storage.upload_multipart(file_metadata.generate_file_parts(file_stream))
        await self._repository.update(file_metadata.id, status=...)
        return file_metadata.id
