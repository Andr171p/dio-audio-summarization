from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat, PositiveInt

from .domain import StrPrimitive
from .utils import current_datetime

# Пороговое значения для размера файла, если больше порога, то файл большой
# и нуждается в потоковой обработке
FILESIZE_MB_THRESHOLD = 100


class Filepath(StrPrimitive):
    """Кастомный примитив для валидации файловых путей.

    Валидирует синтаксис пути без проверки существования файла.
    Поддерживает относительные и абсолютные пути для Unix и Windows.
    """

    MAX_FILEPATH_LENGTH = 4096
    WINDOWS_RESERVED_NAMES: tuple[str, ...] = (
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
        "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3",
        "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    )

    @classmethod
    def validate(cls, filepath: str) -> str:
        if not filepath:
            raise ValueError("Filepath cannot be empty!")
        filepath = filepath.replace("\\", "/")  # Нормализация пути
        cls._check_os_rules(filepath)
        return filepath

    @classmethod
    def _check_os_rules(cls, filepath: str) -> None:
        """Проверка базовых правил для OS"""
        if len(filepath) > cls.MAX_FILEPATH_LENGTH:
            raise ValueError(f"""
                Filepath too long!
                Max length {cls.MAX_FILEPATH_LENGTH}, your length is {len(filepath)}.
            """)
        # Проверка каждой части пути
        for part in filepath.split("/"):
            if not part or part in {".", ".."}:
                continue
            without_ext_part = part.split(".")[0].upper()  # Без расширения
            if without_ext_part in cls.WINDOWS_RESERVED_NAMES:
                raise ValueError(f"Reserved filename: {part}")


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


class FilePart(File):
    """Файловый объект для добавления файла по частям (Multipart upload)

        Attributes:
            part_number: Номер чанка файла.
        """
    part_size: PositiveFloat
    part_number: PositiveInt


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
