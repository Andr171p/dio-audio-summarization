from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from modules.chat.domain import Message

router = APIRouter(prefix="/messages", tags=["Messages 💬"], route_class=DishkaRoute)


@router.get(
    path="/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="Получение сообщения"
)
async def get_message(message_id: UUID) -> Message: ...
