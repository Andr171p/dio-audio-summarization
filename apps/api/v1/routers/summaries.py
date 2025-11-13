from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status

from modules.summarization.application import CreateSummarizationTaskUseCase
from modules.summarization.domain import CreateSummarizationTaskCommand, SummarizationTask

router = APIRouter(prefix="/summaries", tags=["Summaries"], route_class=DishkaRoute)


@router.post(
    path="/tasks",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SummarizationTask,
    summary="Создание задачи на суммаризацию",
)
async def create_summarization_task(
        command: CreateSummarizationTaskCommand, usecase: Depends[CreateSummarizationTaskUseCase]
) -> SummarizationTask:
    return await usecase.execute(command)
