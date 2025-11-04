from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, Form, Request, status
from pydantic import PositiveFloat, PositiveInt

from domains.audio.commands import (
    AddAudioRecordCommand,
    CreateAudioCollectionCommand,
    SummarizeAudioCollectionCommand,
)
from domains.audio.domain import AudioCollection, AudioRecord
from domains.audio.dto import AudioCollectionSummarize
from domains.audio.usecases import AddAudioRecordUseCase, SummarizeAudioCollectionUseCase

router = APIRouter(prefix="/collections", tags=["Audio collections"], route_class=DishkaRoute)


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


@router.get(
    path="/{collection_id}",
    status_code=status.HTTP_200_OK,
    response_model=AudioCollection,
    summary="Получение аудио коллекции по её идентификатору"
)
async def get_collection(collection_id: UUID) -> AudioCollection: ...


@router.post(
    path="/{collection_id}/summarize",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=...,
    summary="Создание задачи на суммаризацию"
)
async def summarize_collection(
        collection_id: UUID,
        schema: AudioCollectionSummarize,
        usecase: Depends[SummarizeAudioCollectionUseCase]
) -> ...:
    command = SummarizeAudioCollectionCommand(
        collection_id=collection_id, summary_type=schema.summary_type
    )
    return await usecase.execute(command)


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


@router.get(
    path="/{collection_id}/records/{record_id}",
    status_code=status.HTTP_200_OK,
    response_model=AudioRecord,
    summary="Получение аудио записи из коллекции"
)
async def get_record(collection_id: UUID, record_id: UUID) -> AudioRecord: ...
