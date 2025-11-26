from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from modules.iam.application import CredentialsAuthService, verify_token
from modules.iam.application.dto import TokenVerify
from modules.iam.domain import TokenPair, User, UserClaims, UserCredentials

router = APIRouter(prefix="", tags=["Credentials Auth"], route_class=DishkaRoute)


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    summary="Регистрация нового пользователя"
)
async def register(
        credentials: UserCredentials, service: FromDishka[CredentialsAuthService]
) -> User:
    return await service.register(credentials)


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenPair,
    summary="Аутентификация пользователя"
)
async def login(
        credentials: UserCredentials, service: FromDishka[CredentialsAuthService]
) -> TokenPair:
    return await service.authenticate(credentials)


@router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    summary="Отзыв токенов"
)
async def logout() -> None: ...


@router.post(
    path="/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenPair,
    summary="Обновление токенов"
)
async def refresh() -> None: ...


@router.post(
    path="/verify",
    status_code=status.HTTP_200_OK,
    response_model=UserClaims,
    response_model_exclude_none=True,
    summary="Верификация токена"
)
async def verify(body: TokenVerify) -> UserClaims:
    return verify_token(body.token)


'''@router.post(
    path="/forgot-password",
    status_code=status.HTTP_200_OK,
    response_model=...,
    summary="Запрос на сброс пароля"
)
async def forgot_password() -> ...: ...


@router.post(
    path="/reset-password",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Сброс и смена пароля"
)
async def reset_password() -> ...: ...'''
