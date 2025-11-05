from uuid import UUID, uuid4

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, Request, status

from modules.audio.application import (
    AddAudioRecordUseCase,
    CreateAudioCollectionUseCase,
    SummarizeAudioCollectionUseCase,
)
from modules.audio.domain import (
    AddAudioRecordCommand,
    AudioCollection,
    AudioRecord,
    CreateAudioCollectionCommand,
    SummarizeAudioCollectionCommand,
    SummarizingState,
)

from ..schemas import AudioMetadataHeaders

router = APIRouter(prefix="/collections", tags=["Audio collections"], route_class=DishkaRoute)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=AudioCollection,
    summary=""
)
async def create_collection(
        command: CreateAudioCollectionCommand, usecase: Depends[CreateAudioCollectionUseCase]
) -> AudioCollection:
    return await usecase.execute(command)


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
    response_model=SummarizingState,
    summary="Создание задачи на суммаризацию"
)
async def summarize_collection(
        collection_id: UUID,
        usecase: Depends[SummarizeAudioCollectionUseCase]
) -> SummarizingState:
    command = SummarizeAudioCollectionCommand(
        collection_id=collection_id, summary_type=...
    )
    return await usecase.execute(command)


@router.post(
    path="/{collection_id}/records/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AudioRecord,
    summary="Потоковая загрузка аудио записи в коллекцию",
)
async def upload_record(
        collection_id: UUID,
        request: Request,
        usecase: Depends[AddAudioRecordUseCase]
) -> AudioRecord:
    headers = AudioMetadataHeaders.model_validate(request.headers)
    command = AddAudioRecordCommand(
        user_id=uuid4(),
        collection_id=collection_id,
        filename=headers.filename,
        filesize=headers.filesize,
        duration=headers.duration,
        channels=headers.channels,
        samplerate=headers.samplerate,
        bitrate=headers.bitrate
    )
    return await usecase.execute(stream=request.stream(), command=command)


@router.get(
    path="/{collection_id}/records/{record_id}",
    status_code=status.HTTP_200_OK,
    response_model=AudioRecord,
    summary="Получение аудио записи из коллекции"
)
async def get_record(collection_id: UUID, record_id: UUID) -> AudioRecord: ...
