from fastapi import APIRouter, status

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post(
    path="/tasks",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=...,
    summary="Создание задачи на суммаризацию",
)
async def create_summarization_task() -> ...: ...
