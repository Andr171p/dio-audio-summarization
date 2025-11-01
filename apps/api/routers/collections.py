from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from domains.audio.domain.commands import AddAudioRecordCommand

router = APIRouter(prefix="/collections", tags=["Audio collections"])


@router.post(
    path="/{collection_id}/records/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="",
)
async def upload_records(
        collection_id: UUID, files: list[UploadFile] = File(...),
) -> ...:
    for file in files:
        command = AddAudioRecordCommand(
            collection_id=collection_id,
            filename=file.filename,
            filesize=file.size,
        )
