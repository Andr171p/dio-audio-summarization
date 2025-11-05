from typing import Self

from fastapi import Request
from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt


class AudioMetadataHeaders(BaseModel):
    filename: str
    filesize: PositiveFloat
    duration: PositiveFloat
    samplerate: PositiveInt | None = None
    channels: PositiveInt | None = None
    bitrate: PositiveInt | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_request(cls, request: Request) -> Self:
        return cls.model_validate(request.headers)
