from typing import Any, Literal, Self

import operator
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

Emotion = Literal["positive", "neutral", "negative"]


class Task(BaseModel):
    id: UUID
    status: Literal["NEW", "RUNNING", "CANCELED", "DONE", "ERROR"]
    created_at: datetime
    updated_at: datetime
    response_file_id: UUID | None = None


class SpeechRecognized(BaseModel):
    text: str
    speaker: int | None = None
    emotion: Emotion

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> Self:
        return cls(
            text=response["results"][0]["normalized_text"],
            speaker=response["speaker_info"]["speaker_id"],
            emotion=cls._parse_emotion(response["emotions_result"]),
        )

    @staticmethod
    def _parse_emotion(emotions_result: dict[Emotion, float]) -> Emotion:
        return max(emotions_result.items(), key=operator.itemgetter(1))[0]
