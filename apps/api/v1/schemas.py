from typing import Annotated, Self

from fastapi import Query, Request
from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt

ChunkSize = Annotated[PositiveInt, Query(...)]
Page = Annotated[PositiveInt, Query(...)]
Limit = Annotated[PositiveInt, Query(...)]


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
