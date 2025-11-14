from typing import Any, Literal, Self

import operator
from collections import UserList
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


class RecognizedSpeech(BaseModel):
    text: str
    speaker: int | None = None
    emotion: Emotion | None = None

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


class RecognizedSpeechList(UserList[RecognizedSpeech]):
    def to_markdown(self) -> str:
        """Приводит распознанную речь в Markdown формат"""
        if not self.data:
            return "No speech recognized"
        lines: list[str] = []
        for i, recognized_speech in enumerate(self.data):
            parts = [f"{i}. {recognized_speech.text}"]
            if recognized_speech.speaker is not None:
                parts.append(f"({recognized_speech.speaker})")
            if recognized_speech.emotion is not None:
                parts.append(f"[{recognized_speech.emotion}]")
            lines.append(" ".join(parts))
        return "\n".join(lines)
