from typing import Any

from uuid import UUID

from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import AggregateRoot, Entity

from .value_objects import AudioFormat


class Meeting(AggregateRoot):
    ...


class Audio(Entity):
    file_id: UUID
    format: AudioFormat
    duration: PositiveInt
    channels: PositiveInt | None = None
    samplerate: PositiveInt | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
