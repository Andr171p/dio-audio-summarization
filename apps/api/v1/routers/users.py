from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from modules.iam.application import UserRepository
from modules.iam.domain import User
from modules.iam.infrastructure.fastapi import CurrentUserDep
from modules.shared_kernel.application.exceptions import NotFoundError

router = APIRouter(prefix="/users", tags=["Users 👤"], route_class=DishkaRoute)


@router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Получить данные о себе"
)
async def get_me(
        current_user: CurrentUserDep, repository: FromDishka[UserRepository]
) -> User:
    user = await repository.read(current_user.user_id)
    if user is None:
        raise NotFoundError(f"User {user} not found", entity_name=User.__class__.__name__)
    return user


@router.post(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=User,
    summary="Получение пользователя",
)
async def get_user(user_id: UUID, repository: FromDishka[UserRepository]) -> User:
    user = await repository.read(user_id)
    if user is None:
        raise NotFoundError(
            f"User {user} not found", entity_name=User.__class__.__name__
        )
    return user
