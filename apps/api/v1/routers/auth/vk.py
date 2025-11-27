from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status

from modules.iam.application import VKAuthService
from modules.iam.application.dto import VKCallback
from modules.iam.domain import TokenPair, User

router = APIRouter(prefix="/vk", tags=["VK Auth"], route_class=DishkaRoute)


@router.get(
    path="/init",
    status_code=status.HTTP_200_OK,
    summary="Инициация аутентификации через ВК"
)
async def init(response: Response, service: FromDishka[VKAuthService]) -> str:
    flow = await service.init_oauth_flow()
    response.set_cookie(
        key="pkce_session_id",
        value=flow.pkce_session_id,
        httponly=False,  # Только для теста
        secure=False,  # Только для теста
        samesite="lax",
        max_age=600  # 10 минут
    )
    return flow.authorization_url


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    summary="Регистрация пользователя"
)
async def register(
        request: Request, callback: VKCallback, service: FromDishka[VKAuthService]
) -> User:
    session_id = request.cookies.get("pkce_session_id")
    return await service.register(session_id, callback)


@router.post(
    path="/authenticate",
    status_code=status.HTTP_200_OK,
    response_model=TokenPair,
    summary="Аутентификация пользователя"
)
async def authenticate(
        request: Request,
        response: Response,
        callback: VKCallback,
        service: FromDishka[VKAuthService]
) -> TokenPair:
    session_id = request.cookies.get("pkce_session_id")
    token_pair = await service.authenticate(session_id, callback)
    response.delete_cookie("pkce_session_id")
    return token_pair
