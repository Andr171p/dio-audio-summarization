from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from modules.admin.application import CreateWorkspaceUseCase, WorkspaceRepository
from modules.admin.application.dto import SentInvitation, WorkspaceCreate
from modules.admin.domain import CreateWorkspaceCommand, Workspace
from modules.iam.infrastructure.fastapi import CurrentUserDep

router = APIRouter(prefix="/workspaces", tags=["Workspaces"], route_class=DishkaRoute)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=list[Workspace],
    summary="Получить мои рабочие области",
)
async def get_my_workspaces(
        current_user: CurrentUserDep, repository: FromDishka[WorkspaceRepository]
) -> list[Workspace]:
    return await repository.get_by_owner(current_user.user_id)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Workspace,
    summary="Создание рабочей области",
)
async def create_workspace(
        current_user: CurrentUserDep,
        body: WorkspaceCreate,
        usecase: FromDishka[CreateWorkspaceUseCase]
) -> Workspace:
    command = CreateWorkspaceCommand.model_validate({
        "user_id": current_user.user_id, **body.model_dump()
    })
    return await usecase.execute(command)


@router.post(
    path="/{workspace_id}/invitations",
    status_code=status.HTTP_201_CREATED,
    response_model=SentInvitation,
    summary="Приглашает участника в рабочую область",
)
async def invite_to_workspace() -> SentInvitation: ...


@router.post(
    path="/{workspace_id}/invitations/accept/{token}",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Принять приглашение",
)
async def accept_invitation() -> ...: ...
