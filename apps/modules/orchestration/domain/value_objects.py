from pydantic import BaseModel, ConfigDict, PositiveFloat, PositiveInt


class AudioChunk(BaseModel):
    number: PositiveInt
    content: bytes
    format: str
    size: PositiveInt
    duration: PositiveFloat

    model_config = ConfigDict(frozen=True)
