from uuid import UUID

from pydantic import BaseModel

from domains.shared_kernel.domain import Entity, FileMetadata, Filepath


class SpeechSegment(BaseModel):
    text: str
    speaker: str | None = None
    emotion: str | None = None


class Transcription(Entity):
    collection_id: UUID
    record_id: UUID
    language: ...
    speech_segments: list[SpeechSegment]


class Summary(Entity):
    """Суммаризация аудио

    Attributes:
        collection_id: Аудио-коллекция к которой принадлежит суммаризация
        title: Заголовок/название самари
        text: Текст в формате Markdown
        filepath: Путь до файла в хранилище (файл в формате pdf, docx, txt)
        metadata: Мета-данные файла
    """
    collection_id: UUID
    title: str
    text: str
    filepath: Filepath
    metadata: FileMetadata
