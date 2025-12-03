from typing import Annotated

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Body, status

from modules.chat.application import ChatRepository
from modules.chat.domain import Chat
from modules.iam.infrastructure.fastapi import CurrentUserDep

router = APIRouter(prefix="/chats", tags=["Chat"], route_class=DishkaRoute)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=list[Chat],
    summary="Мои чаты",
)
async def get_my_chats(
        current_user: CurrentUserDep, repository: FromDishka[ChatRepository]
) -> list[Chat]:
    return await repository.get_by_user(current_user.user_id)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Chat,
    summary="Создать чат для"
)
async def create_chat(
        current_user: CurrentUserDep,
        title: Annotated[str, Body(..., embed=True, description="Название чата")]
) -> Chat:
    ...


@router.get(
    path="/{chat_id}",
    status_code=status.HTTP_200_OK,
    response_model=Chat,
    summary="Получить чат"
)
async def get_chat(chat_id: UUID, repository: FromDishka[ChatRepository]) -> Chat:
    return await repository.read(chat_id)


@router.delete(
    path="/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить чат"
)
async def delete_chat(chat_id: UUID, repository: FromDishka[ChatRepository]) -> None:
    await repository.delete(chat_id)
