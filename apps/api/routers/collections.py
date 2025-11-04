from uuid import UUID

from fastapi import APIRouter, Form, Request, status
from pydantic import PositiveFloat, PositiveInt

from domains.audio.application.usecases import AddAudioRecordUseCase
from domains.audio.domain.aggregates import AudioCollection
from domains.audio.domain.commands import AddAudioRecordCommand, CreateAudioCollectionCommand

router = APIRouter(prefix="/collections", tags=["Audio collections"])


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary=""
)
async def create_collection(command: CreateAudioCollectionCommand) -> AudioCollection:
    ...


@router.get(
    path="/my",
    status_code=status.HTTP_200_OK,
    response_model=list[AudioCollection],
    summary="Получение аудио коллекций пользователя"
)
async def get_my_collections() -> list[AudioCollection]: ...


@router.post(
    path="/{collection_id}/records/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=...,
    summary="Загрузка аудио записи в коллекцию",
)
async def upload_record(
        usecase: AddAudioRecordUseCase,
        request: Request,
        collection_id: UUID,
        filename: str = Form(..., description="Имя файла пользователя"),
        filesize: PositiveFloat = Form(..., description="Размер файла в мб"),
        duration: PositiveFloat = Form(..., description="Продолжительность в секундах"),
        channels: PositiveInt = Form(..., description="Количество каналов"),
        samplerate: PositiveFloat = Form(..., description="Частота дискретизации"),
) -> ...:
    command = AddAudioRecordCommand(
        user_id=...,
        collection_id=collection_id,
        filename=filename,
        filesize=filesize,
        duration=duration,
        channels=channels,
        samplerate=samplerate
    )
    return await usecase.execute(stream=request.stream(), command=command)
