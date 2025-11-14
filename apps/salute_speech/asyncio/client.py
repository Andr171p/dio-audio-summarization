import json
import logging
from uuid import UUID

import aiohttp

from ..constants import AUDIO_ENCODING_CONFIG, SALUTE_SPEECH_BASE_URL, AudioEncoding, Language
from ..exceptions import DownloadingFileError, TaskFailedError, UploadingFileError
from ..models import RecognizedSpeech, RecognizedSpeechList, Task
from .oauth import AsyncOAuthSberDevicesClient

logger = logging.getLogger(__name__)


class AsyncSaluteSpeechClient:
    def __init__(
            self,
            apikey: str,
            scope: str,
            model: str = "general",
            profanity_check: bool = False,
            base_url: str = SALUTE_SPEECH_BASE_URL,
            use_ssl: bool = False,
    ) -> None:
        self._model = model
        self._profanity_check = profanity_check
        self._base_url = base_url
        self._use_ssl = use_ssl
        self._oauth_client = AsyncOAuthSberDevicesClient(
            apikey=apikey, scope=scope, use_ssl=use_ssl
        )

    async def upload_file(
            self,
            file: bytes,
            audio_encoding: AudioEncoding,
            channels: int = 1,
            samplerate: int | None = None
    ) -> UUID:
        if samplerate is None:
            samplerate = 16000
        access_token = await self._oauth_client.authenticate()
        config = AUDIO_ENCODING_CONFIG.get(audio_encoding)
        if config is None:
            raise ValueError(
                f"Unsupported audio encoding format! Input format {audio_encoding},"
                f"supported formats {", ".join(list(AUDIO_ENCODING_CONFIG.keys()))}"
            )
        if channels > config["max_channels"]:
            raise ValueError(
                f"Format {audio_encoding} supports max {config['max_channels']} "
                f"channels, but got {channels}"
            )
        if config["samplerate_range"] is not None:
            min_samplerate, max_samplerate = config["samplerate_range"]
            if not (min_samplerate < samplerate < max_samplerate):
                raise ValueError(
                    f"Format {audio_encoding} requires sample rate between "
                    f"{min_samplerate} and {max_samplerate} Hz, but got {samplerate} Hz"
                )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": config["content_type"].format(samplerate=samplerate),
        }
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.post(
                    url="/data:upload", headers=headers, data=file, ssl=self._use_ssl
            ) as response:
                logger.debug("Start uploading file with format of audio %s", audio_encoding)
                response.raise_for_status()
                data = await response.json()
            return UUID(data["result"]["request_file_id"])
        except aiohttp.ClientResponseError as e:
            error_message = f"Uploading failed with {response.status} status, error: {e}"
            logger.exception(error_message)
            raise UploadingFileError(error_message) from e
        except aiohttp.ClientError as e:
            error_message = f"An unexpected error occurred while uploading file: {e}"
            logger.exception(error_message)
            raise UploadingFileError(error_message) from e

    async def async_recognize(
            self,
            request_file_id: UUID,
            audio_encoding: AudioEncoding,
            diarization: bool = True,
            max_speakers_count: int = 1,
            language: Language = "ru-RU",
            channels: int = 1,
            samplerate: int = 16000,
            words: list[str] | None = None,
            enable_letters: bool = False,
            eou_timeout: int = 1
    ) -> Task:
        """Создание задачи на распознавание.

        :param request_file_id: Идентификатор загруженного файла.
        :param audio_encoding: Аудио-кодек.
        :param diarization: Разделение по спикерам.
        :param max_speakers_count: Максимальное число спикеров.
        :param language: Язык для распознавания речи, доступные языки:
             - ru-RU — русский
             - en-US — английский
             - kk-KZ — казахский
             - ky-KG — киргизский
             - uz-UZ — узбекский.
        :param channels: Количество каналов аудио.
        :param samplerate: Частота дискретизации аудио.
        :param words: Список слов или фраз, распознавание которых мы хотим усилить.
        :param enable_letters: Модель коротких фраз, улучшающая распознавание коротких слов.
        :param eou_timeout: Настройка распознавания конца фразы (End of Utterance — eou).
        :returns: Созданная задача со статусом 'NEW'.
        """
        access_token = await self._oauth_client.authenticate()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Request-ID": f"{request_file_id}",
        }
        payload = {
            "options": {
                "model": self._model,
                "audio_encoding": audio_encoding,
                "sample_rate": samplerate,
                "language": language,
                "enable_profanity_filter": self._profanity_check,
                "channels_count": channels,
                "speaker_separation_options": {
                    "enable": diarization,
                    "enable_only_main_speaker": False,
                    "count": min(max_speakers_count, 10)
                    # Ограничение на максимальное количество спикеров
                }
            },
            # Убираем insight_models для одноканального аудио
            "request_file_id": request_file_id,
        }
        if words:
            payload["hints"] = {
                "words": words,
                "enable_letters": enable_letters,
                "eou_timeout": eou_timeout
            }
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.post(
                    url="/speech/async_recognize",
                    headers=headers,
                    data=json.dumps(payload),
                    ssl=self._use_ssl
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Task.model_validate(data["result"])
        except aiohttp.ClientResponseError as e:
            error_message = f"Task creation failed with status {e.status} error: {e.message}"
            logger.exception(error_message)
            raise TaskFailedError(error_message) from e
        except aiohttp.ClientError as e:
            error_message = f"An error occurred while task creation, error {e}"
            logger.exception(error_message)
            raise TaskFailedError(error_message) from e

    async def get_task_status(self, task_id: UUID) -> Task:
        access_token = await self._oauth_client.authenticate()
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        params = {"id": f"{task_id}"}
        payload = {}
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.get(
                url="/task:get",
                headers=headers,
                params=params,
                data=json.dumps(payload),
                ssl=self._use_ssl
            ) as response:
                response.raise_for_status()
                data = await response.json()
            return Task.model_validate(data["result"])
        except aiohttp.ClientResponseError as e:
            error_message = f"Task receiving failed with status {e.status} error: {e.message}"
            logger.exception(error_message)
            raise TaskFailedError(error_message) from e
        except aiohttp.ClientError as e:
            error_message = f"An error occurred while task receiving, error {e}"
            logger.exception(error_message)
            raise TaskFailedError(error_message) from e

    async def download_file(self, response_file_id: UUID) -> RecognizedSpeechList:
        access_token = await self._oauth_client.authenticate()
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/octet-stream"}
        params = {"response_file_id": f"{response_file_id}"}
        payload = {}
        try:
            async with aiohttp.ClientSession(base_url=self._base_url) as session, session.get(
                url="/data:download",
                headers=headers,
                params=params,
                data=payload,
                ssl=self._use_ssl
            ) as response:
                response.raise_for_status()
                data = await response.text()
            results = json.loads(data)
            return RecognizedSpeechList(
                [RecognizedSpeech.from_response(result) for result in results]
            )
        except aiohttp.ClientResponseError as e:
            error_message = f"Downloading failed with status {e.status} error: {e.message}"
            logger.exception(error_message)
            raise DownloadingFileError(error_message) from e
        except aiohttp.ClientError as e:
            error_message = f"An error occurred while downloading, error {e}"
            logger.exception(error_message)
            raise DownloadingFileError(error_message) from e
