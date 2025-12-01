from datetime import datetime

from pydantic import Field, NonPositiveInt, PositiveInt

from modules.shared_kernel.domain import Entity
from modules.shared_kernel.utils import current_datetime

from .primitives import Filename, Filepath, MimeType
from .value_objects import FileType


class FileMetadata(Entity):
    """Файловые метаданные, несут только информацию о файле

    Attributes:
        filename: Оригинальное имя файла (то которое указал пользователь).
        filepath: Путь до файла в системе.
        filesize: Размер файла в байтах.
        mime_type: MIME-тип файла, например: 'audio/mpeg', 'image/png', ...
        extension: Расширение файла, пример: txt, mp3, pdf, ...
        type: Тип файла, например: image, document, video, audio, ...
        uploaded_at: Дата и время загрузки файла
    """

    filename: Filename
    filepath: Filepath
    filesize: PositiveInt
    mime_type: MimeType
    extension: str
    type: FileType
    uploaded_at: datetime = Field(default_factory=current_datetime)


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
