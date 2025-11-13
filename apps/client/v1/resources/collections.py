import logging
from collections.abc import AsyncIterable
from uuid import UUID

import aiohttp

from ..exceptions import NOT_FOUND_STATUS, ClientError, NotFoundError
from ..schemas import Collection, Record

logger = logging.getLogger(__name__)


class CollectionsResource:
    def __init__(self, route_path: str, timeout: int = 3600) -> None:
        """REST API ресурс аудио коллекций

        :param route_path: URL маршрут до коллекций.
        :param timeout: Тайм-аут для долгих операций, например загрузка файла.
        """
        self._route_path = route_path
        self._timeout = timeout

    async def create(self, user_id: UUID, name: str) -> Collection:
        try:
            logger.debug("Start creating '%s' collection", name)
            async with aiohttp.ClientSession(base_url=self._route_path) as session, session.post(
                json={"user_id": user_id, "topic": name}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info("Collection '%s' created successfully", name)
            return Collection.model_validate(data)
        except aiohttp.ClientResponseError as e:
            error_message = f"Error while creation collection, error message: {e.message}"
            logger.exception(error_message)
            raise ClientError(error_message, status_code=e.status, response=data) from e
        except aiohttp.ClientError as e:
            error_message = f"An unexpected error occurred while collection creation, details: {e}"
            logger.exception(error_message, extra={"status_code": response.status})
            raise ClientError(error_message, status_code=response.status) from e

    async def get(self, collection_id: UUID) -> Collection:
        """Получение аудио коллекции по её идентификатору"""
        try:
            logger.debug("Start getting '%s' collection", collection_id)
            async with aiohttp.ClientSession(base_url=self._route_path) as session, session.post(
                url=f"/{collection_id}"
            ) as response:
                if response.status == NOT_FOUND_STATUS:
                    raise NotFoundError(
                        f"Collection not found by id {collection_id}",
                        status_code=response.status, response_data=await response.json()
                    )
                response.raise_for_status()
                data = await response.json()
                logger.info(
                    "Collection '%s' getting successfully", collection_id, extra=data,
                )
            return Collection.model_validate(data)
        except aiohttp.ClientResponseError as e:
            error_message = f"Error while getting collection, error message: {e.message}"
            logger.exception(error_message)
            raise ClientError(error_message, status_code=e.status, response=data) from e
        except aiohttp.ClientError as e:
            error_message = (
                f"An unexpected error occurred while getting collection, "
                f"details: {e}"
            )
            logger.exception(error_message, extra={"status_code": response.status})
            raise ClientError(error_message, status_code=response.status) from e

    async def upload_record(
            self,
            collection_id: UUID,
            file: AsyncIterable[bytes],
            filename: str,
            filesize: float,
            duration: float,
            channels: int | None = None,
            samplerate: int | None = None,
            bitrate: int | None = None,
    ) -> Record:
        """Потоковая загрузка аудио записи в коллекцию.

        :param collection_id: Идентификатор коллекции.
        :param file: Поток байтов аудио файла.
        :param filename: Оригинальное имя файла.
        :param filesize: Размер файла в байтах.
        :param duration: Продолжительность аудио записи в секундах.
        :param channels: Количество аудио каналов.
        :param samplerate: Частота дискретизации.
        :param bitrate: Бит-рейт.
        :returns: Созданные аудио запись.
        """
        headers: dict[str, str] = {
            "filename": filename, "filesize": f"{filesize}", "duration": f"{duration}"
        }
        if channels is not None:
            headers["channels"] = f"{channels}"
        if samplerate is not None:
            headers["samplerate"] = f"{samplerate}"
        if bitrate is not None:
            headers["bitrate"] = f"{bitrate}"
        try:
            logger.info("Start uploading '%s' record", filename, extra=headers)
            async with aiohttp.ClientSession(
                    base_url=self._route_path, timeout=aiohttp.ClientTimeout(total=self._timeout)
            ) as session, session.post(
                url=f"{collection_id}/records/upload", headers=headers, data=file
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info("Record %s uploading successfully", filename, extra=data)
            return Record.model_validate(data)
        except aiohttp.ClientResponseError as e:
            error_message = f"Error while uploading record, error message: {e.message}"
            logger.exception(error_message)
            raise ClientError(error_message, status_code=e.status, response=data) from e
        except aiohttp.ClientError as e:
            error_message = (
                f"An unexpected error occurred while uploading record, "
                f"details: {e}"
            )
            logger.exception(error_message, extra={"status_code": response.status})
            raise ClientError(error_message, status_code=response.status) from e

    async def get_record(self, record_id: UUID) -> Record:
        """Получение конкретной аудио записи"""
        try:
            async with aiohttp.ClientSession(base_url=self._route_path) as session, session.get(
                url=f"/records/{record_id}"
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Record.model_validate(data)
        except aiohttp.ClientError:
            ...

    async def download_record(
            self, record_id: UUID, chunk_size: int = 8192
    ) -> AsyncIterable[bytes]:
        """Скачивание аудио записи.

        :param record_id: Идентификатор записи.
        :param chunk_size: Размер чанка для оптимального скачивания по частям.
        :returns: Поток байтов аудио файла.
        """
        params = {"chunk_size": chunk_size}
        try:
            async with aiohttp.ClientSession(base_url=self._route_path) as session, session.get(
                url=f"/records/{record_id}/download", params=params
            ) as response:
                response.raise_for_status()
                async for chunk in response.content.iter_chunks(chunk_size):
                    yield chunk
        except aiohttp.ClientError:
            ...
