from uuid import UUID

from fastapi import APIRouter, status

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary=""
)
async def create_chat() -> ...: ...


@router.get(
    path="/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
    response_model=...,
    summary="",
)
async def get_messages(chat_id: UUID) -> ...:
    ...
