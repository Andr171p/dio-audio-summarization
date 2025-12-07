import logging
import math
from collections.abc import AsyncGenerator, AsyncIterable, AsyncIterator
from contextlib import asynccontextmanager

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from ...application import RemoteStorage
from ...application.exceptions import (
    DownloadFailedError,
    RemovingFailedError,
    UploadingFailedError,
)
from ...domain import File, FilePart, Filepath

logger = logging.getLogger(__name__)


class S3Storage(RemoteStorage):
    """Реализация S3 хранилища"""

    def __init__(
            self,
            endpoint_url: str,
            access_key: str,
            secret_key: str,
            bucket: str,
            use_ssl: bool = False
    ) -> None:
        self.config: dict[str, str] = {
            "endpoint_url": endpoint_url,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "use_ssl": use_ssl,
            "region_name": "us-east-1",
            "service_name": "s3",
        }
        self.bucket = bucket
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AioBaseClient]:
        async with self.session.create_client(**self.config) as client:
            yield client

    async def upload(self, file: File) -> None:
        try:
            async with self._get_client() as client:
                await client.put_object(
                    Bucket=self.bucket, Key=file.path, Body=file.content
                )
        except ClientError as e:
            raise UploadingFailedError(
                f"File uploading failed with error: {e}",
                details={"filepath": file.path, "filesize": file.size},
                original_error=e
            ) from e

    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None:
        try:
            upload_id: str | None = None
            parts: list[dict[str, int | str]] = []
            async with self._get_client() as client:
                async for file_part in file_parts:
                    if upload_id is None:
                        response = await client.create_multipart_upload(
                            Bucket=self.bucket, Key=file_part.path
                        )
                        upload_id = response["UploadId"]
                        logger.info(
                            "Initiate multipart uploading",
                            extra={
                                "upload_id": upload_id,
                                "filepath": file_part.path,
                                "filesize": file_part.size,
                            }
                        )
                    part_response = await client.upload_part(
                        Bucket=self.bucket,
                        Key=file_part.path,
                        UploadId=upload_id,
                        PartNumber=file_part.number,
                        Body=file_part.content
                    )
                    parts.append({
                        "PartNumber": file_part.number, "ETag": part_response["ETag"]
                    })
                    logger.info(
                        "Successful upload file part with number %s", file_part.number,
                        extra={"upload_id": upload_id, "etag": part_response["ETag"]},
                    )
                await client.complete_multipart_upload(
                    Bucket=self.bucket,
                    Key=file_part.path,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts}
                )
                logger.info(
                    "Multipart upload completed for %s", len(parts),
                    extra={"upload_id": upload_id, "part_count": len(parts)},
                )
        except ClientError as e:
            raise UploadingFailedError(
                f"Multipart upload failed with error: {e}",
                details={"filepath": file_part.path, "filesize": file_part.size},
                original_error=e
            ) from e

    async def download(self, filepath: Filepath) -> File | None:
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket, Key=filepath)
                content = await response["Body"].read()
                return File(
                    path=filepath,
                    size=response["ContentLength"],
                    mime_type=response["ContentType"],
                    content=content,
                    uploaded_at=response["LastModified"]
                )
        except ClientError as e:
            raise DownloadFailedError(
                f"File download failed with error: {e}",
                details={"filepath": filepath},
                original_error=e
            ) from e

    async def download_multipart(
            self, filepath: Filepath, part_size: int
    ) -> AsyncIterator[FilePart]:
        try:
            async with self._get_client() as client:
                head = await client.head_object(Bucket=self.bucket, Key=filepath)
                filesize, mime_type, uploaded_at = (
                    head["ContentLength"], head["ContentType"], head["LastModified"]
                )
                part_numbers = math.ceil(filesize / part_size)
                logger.info(
                    "Start multipart downloading file, filesize %s, total parts %s",
                    filesize, part_numbers
                )
                for part_number in range(part_numbers):
                    start = part_number * part_size
                    end = min((part_number + 1) * part_size - 1, filesize - 1)
                    logger.info(
                        "Downloading part %s: bytes %s-%s", part_number, start, end
                    )
                    response = await client.get_object(
                        Bucket=self.bucket, Key=filepath, Range=f"bytes={start}-{end}"
                    )
                    content = await response["Body"].read()
                    yield FilePart(
                        number=part_number,
                        total_size=filesize,
                        total_parts=part_numbers,
                        path=filepath,
                        size=len(content),
                        mime_type=mime_type,
                        content=content,
                        uploaded_at=uploaded_at,
                    )
        except ClientError as e:
            raise DownloadFailedError(
                f"File multipart downloading failed with error: {e}",
                details={"filepath": filepath, "part_size": part_size},
                original_error=e
            ) from e

    async def remove(self, filepath: Filepath) -> bool:
        try:
            async with self._get_client() as client:
                response = await client.delete_object(Bucket=self.bucket, Key=filepath)
        except ClientError as e:
            raise RemovingFailedError(
                f"File remove failed with error: {e}",
                details={"filepath": filepath},
                original_error=e
            ) from e
        else:
            return ...

    async def exists(self, filepath: Filepath) -> bool: ...

    async def generate_presigned_url(
            self, filepath: Filepath, expires_in: int = 60 * 60
    ) -> str:
        try:
            async with self._get_client() as client:
                return await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": filepath},
                    ExpiresIn=expires_in
                )
        except ClientError:
            ...
