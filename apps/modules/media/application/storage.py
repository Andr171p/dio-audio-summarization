from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from ..domain import File, FilePart, Filepath


class Storage(ABC):
    """Файловое/объектное хранилище"""

    @abstractmethod
    async def upload(self, file: File) -> None:
        """Загрузка файла в хранилище"""

    @abstractmethod
    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None:
        """Загрузка файла по частым в хранилище

        :param file_parts: Асинхронный генератор для оптимизации памяти.
        """

    @abstractmethod
    async def download(self, filepath: Filepath) -> File | None:
        """Скачивание файла из хранилища

        :param filepath: Системный путь до файла.
        """

    @abstractmethod
    async def download_multipart(
            self, filepath: Filepath, part_size: int
    ) -> AsyncIterable[FilePart]:
        """Скачивание файла по частым их хранилища

        :param filepath: Системный путь до файла.
        :param part_size: Размер чанка для скачивания.
        :returns: Асинхронный генератор файловых чанков.
        """

    @abstractmethod
    async def remove(self, filepath: Filepath) -> bool:
        """Удаление файла из хранилища"""

    @abstractmethod
    async def exists(self, filepath: Filepath) -> bool:
        """Проверка наличия файла без его загрузки"""

    @abstractmethod
    async def generate_presigned_url(
            self, filepath: Filepath, expires_in: int = 60 * 60
    ) -> str:
        """Генерация пред-подписанного URL для безопасного скачивания (доступно только для S3)

        :param filepath: Системный путь до файла в хранилище.
        :param expires_in: Промежуток в секундах через который истекает действие URL.
        :returns: Сгенерированный URL.
        """
