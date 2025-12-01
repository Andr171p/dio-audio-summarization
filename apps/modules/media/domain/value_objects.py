from enum import StrEnum


class FileType(StrEnum):
    """Тип контента файла, 'other' если тип файла не распознан"""

    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"
