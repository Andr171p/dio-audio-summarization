from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat

from ..utils import current_datetime
from .primitives import Filepath


class File(BaseModel):
    """Файловый объект (использовать для работы с хранилищем и прочей работы с файлами)

    Attributes:
        filepath: Путь до файла в системе (s3, local, http, ...)
        filesize: Размер файла в байтах.
        content: Содержимое файла в байтовом формате.
        uploaded_at: Дата и время загрузки файла.
    """
    filepath: Filepath
    filesize: PositiveFloat
    content: bytes
    uploaded_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True, frozen=True)


class FileType(StrEnum):
    """Тип контента файла"""
    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"


class FileMetadata(BaseModel):
    """Файловые метаданные

    Attributes:
        filename: Оригинальное имя файла (то которое указал пользователь)
        filesize: Размер файла в байтах
        format: Формат файла, пример: txt, mp3, pdf, ...
        type: Тип файла, например: image, document, video, audio, ...
        uploaded_at: Дата и время загрузки файла
    """
    filename: str
    filesize: PositiveFloat
    format: str
    type: FileType
    uploaded_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True)
