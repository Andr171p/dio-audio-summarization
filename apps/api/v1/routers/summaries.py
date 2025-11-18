from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status

from modules.summarization.application import CreateTaskUseCase, TaskRepository
from modules.summarization.domain import CreateSummarizationTaskCommand, SummarizationTask, Summary

router = APIRouter(prefix="/summaries", tags=["Summaries"], route_class=DishkaRoute)


@router.post(
    path="/tasks",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SummarizationTask,
    summary="Создание задачи на суммаризацию",
)
async def create_summarization_task(
        command: CreateSummarizationTaskCommand, usecase: Depends[CreateTaskUseCase]
) -> SummarizationTask:
    return await usecase.execute(command)


@router.get(
    path="/{summary_id}",
    status_code=status.HTTP_200_OK,
    response_model=Summary,
    summary="Получение метаданных саммари"
)
async def get_summary(summary_id: UUID) -> Summary:
    ...


'''@router.get(
    path="/{summary_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Скачивание документа с саммари"
)
async def download_summary(summary_id: UUID) -> ...: ...


@router.get(
    path="/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=SummarizationTask,
    summary="Получение текущей задачи на суммаризацию"
)
async def get_summarization_task(
        task_id: UUID, repository: Depends[TaskRepository]
) -> SummarizationTask:
    return await repository.read(task_id)'''
