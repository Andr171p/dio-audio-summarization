from typing import Annotated

from collections.abc import AsyncIterator
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import PositiveInt

from modules.media.application import DownloadFileQuery, MediaService
from modules.media.application.dto import FileHeaders
from modules.media.domain import FileMetadata, UploadFileCommand

router = APIRouter(prefix="/files", tags=["Files 📁"], route_class=DishkaRoute)

ChunkSize = Annotated[PositiveInt, Query(..., description="Размер чанка для скачивания")]


@router.post(
    path="/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=FileMetadata,
    summary="Потоковая загрузка файла на сервер",
)
async def upload_file(
        headers: FileHeaders, request: Request, service: FromDishka[MediaService]
) -> FileMetadata:
    command = UploadFileCommand.model_validate(headers)
    return await service.upload_file(command, request.stream())


@router.get(
    path="/{file_id}",
    status_code=status.HTTP_200_OK,
    response_model=FileMetadata,
    summary="Получение мета-данных файла"
)
async def get_file_metadata(file_id: UUID, service: FromDishka[MediaService]) -> FileMetadata:
    return await service.get_file_metadata(file_id)


@router.delete(
    path="/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление файла"
)
async def remove_file(file_id: UUID, service: FromDishka[MediaService]) -> None:
    return await service.remove_file(file_id)


@router.get(
    path="/{file_id}/download",
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
    summary="Потоковое скачивание файла",
)
async def download_file(
        file_id: UUID,
        chunk_size: ChunkSize,
        service: FromDishka[MediaService]
) -> StreamingResponse:
    file_metadata = await service.get_file_metadata(file_id)
    query = DownloadFileQuery(file_id=file_id, chunk_size=chunk_size)

    async def file_content_generator() -> AsyncIterator[bytes]:
        async for file_part in service.download_file(query):
            yield file_part.content

    headers = {
        "Content-Type": f"{file_metadata.mime_type}",
        "Content-Length": f"{file_metadata.filesize}",
        "Content-Disposition": f'attachment; filename="{file_metadata.filename}"',
        "Transfer-Encoding": "chunked",
        "X-Content-Type-Options": "nosniff",
    }
    return StreamingResponse(
        file_content_generator(), media_type="application/octet-stream", headers=headers
    )
