from typing import Self

import math
from collections.abc import AsyncIterable
from datetime import datetime
from uuid import uuid4

from pydantic import Field, NonPositiveInt, PositiveInt

from modules.shared_kernel.domain import Entity
from modules.shared_kernel.utils import current_datetime

from .primitives import Filename, Filepath, MimeType
from .value_objects import FileStatus, FileType


class File(Entity):
    """Файловый объект (использовать для работы с хранилищем и прочей работы с файлами)

    Attributes:
        path: Путь до файла в системе (s3, local, http, ...)
        size: Размер файла в байтах.
        mime_type: MIME-тип файла.
        content: Содержимое файла в байтовом формате.
        uploaded_at: Дата и время загрузки файла.
    """

    path: Filepath
    size: PositiveInt
    mime_type: MimeType
    content: bytes
    uploaded_at: datetime = Field(default_factory=current_datetime)


class FilePart(File):
    """Файловый объект для добавления файла по частям (Multipart upload)

    Attributes:
        number: Номер чанка файла.
        total_size: Общий объём полного файла.
        total_parts: Общее количество частей.
    """

    number: NonPositiveInt
    total_size: PositiveInt
    total_parts: PositiveInt

    @property
    def is_last(self) -> bool:
        """Является ли чанк последним"""
        return self.number == self.total_parts

    @property
    def progress_percentage(self) -> float:
        """Процент выполнения загрузки файла"""
        if self.total_size > 0:
            uploaded = self.number * self.size
            return (uploaded / self.total_size) * 100
        return 0.0


class FileMetadata(Entity):
    """Файловые метаданные, несут только информацию о файле

    Attributes:
        status: Статус загрузки файла, при создании 'uploading'.
        filename: Оригинальное имя файла (то которое указал пользователь).
        filepath: Путь до файла в системе.
        filesize: Размер файла в байтах.
        mime_type: MIME-тип файла, например: 'audio/mpeg', 'image/png', ...
        extension: Расширение файла, пример: txt, mp3, pdf, ...
        type: Тип файла, например: image, document, video, audio, ...
        uploaded_at: Дата и время загрузки файла
    """

    status: FileStatus
    filename: Filename
    filepath: Filepath
    filesize: PositiveInt
    mime_type: MimeType
    extension: str
    type: FileType
    uploaded_at: datetime = Field(default_factory=current_datetime)

    @classmethod
    def create(
            cls,
            filename: str,
            mime_type: str,
            filesize: int,
            /,
            tenant: str,
            entity_type: str,
            entity_id: str,
    ) -> Self:
        """Создание мета-данных файла.

        :param filename: Оригинальное имя файла.
        :param mime_type: MIME-тип файла, передаётся пользователем.
        :param filesize: Размер файла в байтах.
        :param tenant: Клиент, компания, область.
        :param entity_type: Тип сущности, которой принадлежит файл, например: 'user', 'message'.
        :param entity_id: Идентификатор сущности за которой закреплён файл.
        """

        file_id = uuid4()
        filename = Filename(filename)
        mime_type = MimeType(mime_type)
        filepath = Filepath(
            f"{tenant}/{entity_type}/{entity_id}/{mime_type.type}/{file_id}.{filename.extension}"
        )
        return cls(
            id=file_id,
            status=FileStatus.UPLOADING,
            filename=filename,
            filepath=filepath,
            filesize=filesize,
            mime_type=mime_type,
            extension=filename.extension,
            type=mime_type.type,
        )

    async def generate_file_parts(
            self, file_stream: AsyncIterable[bytes], min_part_size: int = 5 * 1024 * 1024
    ) -> AsyncIterable[FilePart]:
        """Асинхронный генератор для потоковой загрузки файла по частям.

        :param file_stream: Байтовых поток файла, которые нужно загрузить.
        :param min_part_size: Минимальный размер части файла (5 mb по умолчанию)
        """
        total_parts = math.ceil(self.filesize / min_part_size)
        part_number = 1
        buffer = b""
        async for chunk in file_stream:
            buffer += chunk
            while len(buffer) >= min_part_size:
                content_part = buffer[:min_part_size]
                buffer = buffer[min_part_size:]
                yield FilePart(
                    number=part_number,
                    total_size=self.filesize,
                    total_parts=total_parts,
                    path=self.filepath,
                    size=len(content_part),
                    mime_type=self.mime_type,
                    content=content_part,
                    uploaded_at=self.uploaded_at,
                )
            part_number += 1
        # Отправка оставшихся данных (последняя часть может быть меньше min_part_size)
        if buffer:
            yield FilePart(
                number=part_number,
                total_size=self.filesize,
                total_parts=total_parts,
                path=self.filepath,
                size=self.filesize,
                mime_type=self.mime_type,
                content=buffer,
                uploaded_at=self.uploaded_at,
            )
