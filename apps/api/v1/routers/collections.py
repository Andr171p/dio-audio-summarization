from collections.abc import AsyncIterable
from uuid import UUID, uuid4

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from modules.audio.application import (
    CollectionRepository,
    CreateCollectionUseCase,
    UploadRecordUseCase,
)
from modules.audio.domain import (
    AddRecordCommand,
    AudioCollection,
    AudioRecord,
    CreateCollectionCommand,
)
from modules.shared_kernel.application import Storage

from ..schemas import AudioMetadataHeaders, ChunkSize

router = APIRouter(prefix="/collections", tags=["Audio collections"], route_class=DishkaRoute)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=AudioCollection,
    summary=""
)
async def create_collection(
        command: CreateCollectionCommand, usecase: Depends[CreateCollectionUseCase]
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
async def get_collection(
        collection_id: UUID, repository: Depends[CollectionRepository]
) -> AudioCollection:
    return await repository.read(collection_id)


@router.post(
    path="/{collection_id}/records/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=AudioRecord,
    summary="Потоковая загрузка аудио записи в коллекцию",
)
async def upload_record(
        collection_id: UUID,
        request: Request,
        usecase: Depends[UploadRecordUseCase]
) -> AudioRecord:
    headers = AudioMetadataHeaders.model_validate(request.headers)
    command = AddRecordCommand(
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
    path="/records/{record_id}",
    status_code=status.HTTP_200_OK,
    response_model=AudioRecord,
    summary="Получение аудио записи из коллекции"
)
async def get_record(record_id: UUID, repository: Depends[CollectionRepository]) -> AudioRecord:
    return await repository.get_record(record_id)


@router.get(
    path="/records/{record_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Скачивание аудио записи",
)
async def download_record(
        record_id: UUID,
        chunk_size: ChunkSize,
        repository: Depends[CollectionRepository],
        storage: Depends[Storage]
) -> StreamingResponse:
    record = await repository.get_record(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    async def content_generator() -> AsyncIterable[bytes]:
        file_parts = storage.download_multipart(record.filepath, part_size=chunk_size)
        async for file_part in file_parts:
            yield file_part.content

    return StreamingResponse(
        content=content_generator(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{record.metadata.filename}"',
            "Content-Type": "audio/mpeg",
        }
    )
