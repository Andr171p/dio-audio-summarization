from typing import Any

from collections.abc import AsyncIterable
from uuid import UUID

from pydantic import Field, PositiveFloat, PositiveInt

from modules.shared_kernel.domain import Entity
from modules.shared_kernel.files import FilePart, Filepath

from .value_objects import AudioFormat


class Meeting(...):
    ...


class Audio(Entity):
    file_id: UUID
    format: AudioFormat
    duration: PositiveInt
    channels: PositiveInt | None = None
    samplerate: PositiveInt | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AudioFile(Entity):
    """Аудио запись"""

    message_id: UUID
    filepath: Filepath
    filesize: PositiveInt
    duration: PositiveFloat
    channels: PositiveInt | None = None
    samplerate: PositiveFloat | None = None
    bitrate: PositiveInt | None = None

    async def generate_file_parts(
            self, stream: AsyncIterable[bytes], min_part_size: PositiveInt = ...
    ) -> AsyncIterable[FilePart]:
        """Асинхронный генератор для потоковой загрузки файла по частям

        :param stream: Байтовых поток файла, которые нужно загрузить.
        :param min_part_size: Минимальный размер части файла.
        """
        part_number = 1
        buffer = b""
        async for chunk in stream:
            buffer += chunk
            while len(buffer) >= min_part_size:
                content_part = buffer[:min_part_size]
                buffer = buffer[min_part_size:]
                yield FilePart(
                    filepath=self.filepath,
                    filesize=self.filesize,
                    content=content_part,
                    part_size=len(content_part),
                    part_number=part_number,
                )
            part_number += 1
        # Отправка оставшихся данных (последняя часть может быть меньше min_part_size)
        if buffer:
            yield FilePart(
                filepath=self.filepath,
                filesize=self.filesize,
                content=buffer,
                part_size=len(buffer),
                part_number=part_number,
            )
