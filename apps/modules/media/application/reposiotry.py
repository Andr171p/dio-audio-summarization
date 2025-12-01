from abc import abstractmethod

from modules.shared_kernel.application import CRUDRepository

from ..domain import FileMetadata, Filepath


class FileMetaRepository(CRUDRepository[FileMetadata]):
    @abstractmethod
    async def get_by_filepath(self, filepath: Filepath) -> FileMetadata | None:
        """Получение мета-данных по уникальному системному пути"""
