from typing import Any, Self

from datetime import datetime
from enum import StrEnum

from pydantic import Field, NonNegativeInt, model_validator

from .domain import Command, Entity, InvariantViolationError
from .utils import current_datetime


class CreateTaskCommand(Command):
    """Команда для создания задачи

    Attributes:
        ...
    """
    task_type: str
    payload: dict[str, Any]
    max_retries: NonNegativeInt


class TaskStatus(StrEnum):
    """Статус задачи"""
    NEW = "new"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Entity):
    type: str
    status: TaskStatus
    payload: dict[str, Any]
    started_at: datetime | None = None
    finished_at: datetime | None = None
    retry_count: NonNegativeInt = Field(default=0)
    max_retries: NonNegativeInt
    failure_reason: str | None = None

    @model_validator(mode="after")
    def _check_invariant_violation(self) -> Self:
        """Проверка состояния инварианта"""
        if self.status == TaskStatus.STARTED and self.started_at is None:
            raise InvariantViolationError(
                "Task cannot be in 'started' status without started_at datetime!",
                entity_name=self.__class__.__name__,
            )
        if self.status in {TaskStatus.COMPLETED, TaskStatus.FAILED} and self.finished_at is None:
            raise InvariantViolationError(
                f"Task cannot be in {self.status} status without finished_at datetime",
                entity_name=self.__class__.__name__,
            )
        return self

    @property
    def execution_time(self) -> float | None:
        """Время выполнения задачи в секундах. Возвращает None если задача не окончена"""
        if self.status not in {TaskStatus.COMPLETED, TaskStatus.FAILED}:
            return None
        return round(self.finished_at.timestamp() - self.started_at.timestamp(), 2)

    def can_retry(self) -> bool:
        """Можно ли перезапустить задачу"""
        return self.retry_count >= self.max_retries

    def increment_retry(self) -> None:
        """Увеличение количества попыток для перезапуска"""
        self.retry_count += 1

    @classmethod
    def create(cls, command: CreateTaskCommand) -> Self:
        """Фабричный метод лля создания задачи"""
        return cls(
            type=command.task_type,
            status=TaskStatus.NEW,
            payload=command.payload,
            max_retries=command.max_retries
        )

    def start(self) -> None:
        """Старт выполнения задачи"""
        self.status = TaskStatus.STARTED
        self.started_at = current_datetime()

    def complete(self) -> None:
        """Успешное завершение выполнение задачи"""
        self.status = TaskStatus.COMPLETED
        self.finished_at = current_datetime()

    def fail(self, reason: str) -> None:
        """Задача закончена с ошибкой

        :param reason: Причина по которой задача завершилась с ошибкой.
        """
        self.status = TaskStatus.FAILED
        self.finished_at = current_datetime()
        self.failure_reason = reason
