from typing import Self

from enum import StrEnum
from uuid import UUID

from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import AggregateRoot, CommandT, EventT

from .commands import (
    EnhanceSoundQualityCommand,
    ProcessAudioCommand,
    SummarizeTranscriptionCommand,
    TranscribeAudioCommand,
)

STEPS = [
    ProcessAudioCommand,
    EnhanceSoundQualityCommand,
    TranscribeAudioCommand,
    SummarizeTranscriptionCommand
]


class TaskStatus(StrEnum):
    NEW = "new"
    PROCESSING = "processing"
    SOUND_ENHANCEMENT = "sound_enhancement"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


class SummarizationTask(AggregateRoot):
    collection_id: UUID
    status: TaskStatus
    total_chunks: PositiveInt = Field(default=1)
    processed_chunks: ...
    _step: list[CommandT]
    _events: list[EventT]

    def _register_step(self, command: CommandT) -> None:
        self._step.append(command)

    @classmethod
    def create(cls, collection_id: UUID) -> Self:
        task = cls(collection_id=collection_id, status=TaskStatus.NEW)
        cls._register_step(task, ProcessAudioCommand(
            collection_id=collection_id,
            output_format="wav",
            chunk_duration=60 * 20,  # 20 Минут
        ))
        return task

    def current_step(self) -> CommandT:
        return self._step[-1]
