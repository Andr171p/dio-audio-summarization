from typing import Annotated

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Body, status

from modules.chat.domain import Chat
from modules.iam.infrastructure.fastapi import CurrentUserDep

router = APIRouter(prefix="/chats", tags=["Chat"], route_class=DishkaRoute)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Chat,
    summary=""
)
async def create_chat(
        current_user: CurrentUserDep,
        title: Annotated[str, Body(..., description="Название чата")]
) -> Chat:
    ...


@router.get(
    path="/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
    response_model=...,
    summary="",
)
async def get_messages(chat_id: UUID) -> ...:
    ...
