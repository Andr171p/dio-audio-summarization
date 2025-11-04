from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from domains.shared_kernel import File, Filepath, Storage
from domains.shared_kernel.domain import FilePart


class S3Storage(Storage):
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
            "service": "s3",
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
                    Bucket=self.bucket, Key=file.filepath, Body=file.content
                )
        except ClientError as e:
            raise UploadingError(f"Error while file uploading, error: {e}") from e

    async def download(self, filepath: Filepath) -> File | None:
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket, Key=filepath)
                content = await response["Body"].read()
                return File(
                    filepath=filepath,
                    content=content,
                    filesize=response["ContentLength"],
                    last_modified=response["LastModified"]
                )
        except ClientError as e:
            raise DownloadingError(f"Error while file downloading, error: {e}") from e

    async def remove(self, filepath: Filepath) -> bool:
        try:
            async with self._get_client() as client:
                response = await client.delete_object(Bucket=self.bucket, Key=filepath)
        except ...:
            ...

    async def exists(self, filepath: Filepath) -> bool: ...

    async def upload_multipart(self, file_parts: AsyncIterable[FilePart]) -> None:
        upload_id: str | None = None
        parts: list[dict[str, int | str]] = []
        async with self._get_client() as client:
            async for file_part in file_parts:
                if upload_id is None:
                    response = await client.create_multipart_upload(
                        Bucket=self.bucket, Key=file_part.filepath
                    )
                    upload_id = response["UploadId"]
                part_response = await client.upload_part(
                    Bucket=self.bucket,
                    Key=file_part.filepath,
                    UploadId=upload_id,
                    PartNumber=file_part.part_number,
                    Body=file_part.content
                )
                parts.append({
                    "PartNumber": file_part.part_number, "ETag": part_response["ETag"]
                })
            client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=file_part.filepath,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )
