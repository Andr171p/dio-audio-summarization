from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from modules.iam.application import CredentialsRegistrationUseCase
from modules.iam.domain import UserCredentials

router = APIRouter(prefix="/registration", tags=["Registration"], route_class=DishkaRoute)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Регистрация нового пользователя",
)
async def register(
        credentials: UserCredentials, usecase: FromDishka[CredentialsRegistrationUseCase]
) -> ...:
    ...
