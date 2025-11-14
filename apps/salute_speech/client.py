import json
import logging
from uuid import UUID

import requests

from .constants import AUDIO_ENCODING_CONFIG, SALUTE_SPEECH_BASE_URL, AudioEncoding, Language
from .exceptions import DownloadingFileError, TaskFailedError, UploadingFileError
from .models import RecognizedSpeech, RecognizedSpeechList, Task
from .oauth import OAuthSberDevicesClient

logger = logging.getLogger(__name__)


class SaluteSpeechClient:
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
        self._oauth_client = OAuthSberDevicesClient(apikey=apikey, scope=scope, use_ssl=use_ssl)

    def upload_file(
            self,
            file: bytes,
            audio_encoding: AudioEncoding,
            channels: int = 1,
            samplerate: int | None = None
    ) -> UUID:
        if samplerate is None:
            samplerate = 16000
        url = f"{self._base_url}/data:upload"
        access_token = self._oauth_client.authenticate()
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
            with requests.Session() as session:
                logger.debug("Start uploading file with format of audio %s", audio_encoding)
                response = session.post(
                    url=url, headers=headers, data=file, verify=False, stream=True
                )
                response.raise_for_status()
                data = response.json()
            return UUID(data["result"]["request_file_id"])
        except requests.exceptions.HTTPError as e:
            error_message = f"Uploading failed with {response.status_code} status, error: {e}"
            raise UploadingFileError(error_message) from e

    def async_recognize(
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
        url = f"{SALUTE_SPEECH_BASE_URL}/speech/async_recognize"
        access_token = self._oauth_client.authenticate()
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
            with requests.Session() as session:
                response = session.post(
                    url=url, headers=headers, data=json.dumps(payload), verify=self._use_ssl
                )
                response.raise_for_status()
                data = response.json()
            return Task.model_validate(data["result"])
        except requests.exceptions.HTTPError as e:
            raise TaskFailedError(
                f"Task creation failed with status {response.status_code} error: {e}"
            ) from e

    def get_task_status(self, task_id: UUID) -> Task:
        url = f"{self._base_url}/task:get"
        access_token = self._oauth_client.authenticate()
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        params = {"id": f"{task_id}"}
        payload = {}
        try:
            with requests.Session() as session:
                response = session.get(
                    url=url,
                    headers=headers,
                    params=params,
                    data=json.dumps(payload),
                    verify=self._use_ssl
                )
                response.raise_for_status()
                data = response.json()
            return Task.model_validate(data["result"])
        except requests.exceptions.HTTPError:
            raise TaskFailedError("Task receiving failed") from None

    def download_file(self, response_file_id: UUID) -> RecognizedSpeechList:
        url = f"{self._base_url}/data:download"
        access_token = self._oauth_client.authenticate()
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/octet-stream"}
        params = {"response_file_id": f"{response_file_id}"}
        payload = {}
        try:
            with requests.Session() as session:
                response = session.get(
                    url=url, headers=headers, params=params, data=payload, verify=self._use_ssl
                )
                response.raise_for_status()
                data = response.text
            results = json.loads(data)
            return RecognizedSpeechList(
                [RecognizedSpeech.from_response(result) for result in results]
            )
        except requests.exceptions.HTTPError as e:
            raise DownloadingFileError(
                f"Downloading failed with status {response.status_code} error: {e}"
            ) from e
