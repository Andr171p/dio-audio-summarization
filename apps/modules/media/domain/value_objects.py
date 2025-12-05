from enum import StrEnum


class FileType(StrEnum):
    """Тип контента файла, 'other' если тип файла не распознан"""

    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"


class FileStatus(StrEnum):
    """Статус файла

    Attributes:
        UPLOADING: В процессе загрузки
        UPLOADED: Загружен в хранилище, но не прикреплён
        ATTACHED: Прикреплён к сущности
    """

    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    TEMPORARY = "temporary"
    ATTACHED = "attached"
    PERMANENT = "permanent"
