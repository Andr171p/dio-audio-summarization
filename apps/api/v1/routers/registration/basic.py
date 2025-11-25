from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from modules.iam.application import RegisterByCredentialsUseCase
from modules.iam.domain import User, UserCredentials

router = APIRouter(prefix="/registration", tags=["Basic Registration"], route_class=DishkaRoute)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    summary="Регистрация нового пользователя",
)
async def register(
        credentials: UserCredentials, usecase: FromDishka[RegisterByCredentialsUseCase]
) -> User:
    return await usecase.execute(credentials)
