from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, status

from modules.iam.application import VKAuthNService
from modules.iam.application.dto import PKCESession, VKCallback
from modules.iam.domain import TokenPair
from modules.iam.infrastructure.oauth import vk_oauth_client

router = APIRouter(prefix="/vk", tags=["VK Auth"], route_class=DishkaRoute)


@router.get(
    path="/init",
    status_code=status.HTTP_200_OK,
    summary="Инициация аутентификации через ВК"
)
async def get_auth_url(request: Request) -> str:
    auth_data = await vk_oauth_client.generate_authorization_url()
    request.session["code_verifier"] = auth_data["code_verifier"]
    request.session["state"] = auth_data["state"]
    return auth_data["authorization_url"]


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Регистрация пользователя"
)
async def register(callback: VKCallback) -> ...: ...


@router.post(
    path="/authenticate",
    status_code=status.HTTP_200_OK,
    response_model=TokenPair,
    summary="Аутентификация пользователя"
)
async def authenticate(
        request: Request, callback: VKCallback, service: FromDishka[VKAuthNService]
) -> TokenPair:
    session = PKCESession(
        code_verifier=request.session.get("code_verifier"), state=request.session.get("state")
    )
    return await service.authenticate(callback, session)
