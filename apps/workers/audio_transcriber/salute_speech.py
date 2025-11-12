from typing import Literal

import base64
import json
import logging
from uuid import UUID, uuid4

import requests

from .exceptions import AuthenticationFailedError, UploadingFileError
from .models import SpeechRecognized, Task

logger = logging.getLogger(__name__)

# Базовый URL сервиса SberDevices
SBER_DEVICES_BASE_URL = "https://ngw.devices.sberbank.ru:9443/api/v2"
# Salute-Speech базовый URL
SALUTE_SPEECH_BASE_URL = "https://smartspeech.sber.ru/rest/v1"

AudioEncoding = Literal["PCM_S16LE", "OPUS", "MP3", "FLAC", "ALAW", "MULAW"]
AUDIO_ENCODING_MAP: dict[str, AudioEncoding] = {
    # PCM форматы
    "wav": "PCM_S16LE",
    "pcm": "PCM_S16LE",
    "wave": "PCM_S16LE",
    # Opus форматы
    "ogg": "OPUS",
    "opus": "OPUS",
    "webm": "OPUS",
    "oga": "OPUS",
    # MP3
    "mp3": "MP3",
    "mpeg": "MP3",
    # FLAC
    "flac": "FLAC",
    # G.711 кодеков
    "alaw": "ALAW",
    "g711alaw": "ALAW",
    "mulaw": "MULAW",
    "g711mulaw": "MULAW",
    "ulaw": "MULAW",  # альтернативное название для MULAW
}


class OAuthSberDevicesClient:
    def __init__(
            self,
            apikey: str,
            scope: str,
            client_id: str,
            client_secret: str,
            use_ssl: bool = False,
    ) -> None:
        self._apikey = apikey
        self._scope = scope
        self._client_id = client_id
        self._client_secret = client_secret
        self._rq_uid = uuid4()
        self._use_ssl = use_ssl

    def _build_apikey(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    def authenticate(self) -> str:
        """Производит аутентификацию клиента, выдавая access token"""
        url = f"{SBER_DEVICES_BASE_URL}/oauth"
        headers = {
            "Authorization": f"Bearer {self._build_apikey()}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": self._rq_uid,
        }
        payload = {"scope": self._scope}
        try:
            with requests.Session() as session:
                logger.debug("Make request for authentication")
                response = session.post(
                    url=url, headers=headers, data=payload, verify=self._use_ssl
                )
                response.raise_for_status()
                data = response.json()
            access_token = data.get("access_token")
            if access_token is None:
                error_message = "Authentication failed, because access token missing in response!"
                logger.error(error_message)
                raise AuthenticationFailedError(error_message)
        except requests.exceptions.HTTPError as e:
            error_message = f"Authentication failed with status {response.status_code}, error: {e}"
            logger.exception(error_message)
            raise AuthenticationFailedError(error_message) from e
        else:
            logger.info("Client successfully authenticated!")
            return access_token


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
        self._oauth_client = OAuthSberDevicesClient(
            apikey=apikey, scope=scope, use_ssl=use_ssl
        )

    def upload_file(self, file: bytes, audio_format: str) -> UUID:  # noqa: A002
        url = f"{self._base_url}/data:upload"
        access_token = self._oauth_client.authenticate()
        headers = {
            "Authorization": f"Bearer {access_token}", "Content-Type": "audio/mpeg",
        }
        try:
            with requests.Session() as session:
                logger.debug("Start uploading file with format of audio %s", audio_format)
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
            audio_format: str,
            diarization: bool = True,
            speaker_count: int = 1,
            language: str = "ru-RU",
            channels_count: int = 1,
            samplerate: int = 16000,
            words: list[str] | None = None,
    ) -> Task:
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
                "audio_encoding": AUDIO_ENCODING_MAP[audio_format],
                "sample_rate": samplerate,
                "language": language,
                "enable_profanity_filter": self._profanity_check,
                "channels_count": channels_count,
                "speaker_separation_options": {
                    "enable": diarization,
                    "enable_only_main_speaker": False,
                    "count": min(speaker_count, 10)
                    # Ограничение на максимальное количество спикеров
                }
            },
            "request_file_id": request_file_id,
        }
        if words:
            payload["hints"] = {
                "words": words,
                "enable_letters": ...,
                "eou_timeout": ...
            }
        try:
            with requests.Session() as session:
                response = session.post(
                    url=url, headers=headers, data=json.dumps(payload), verify=self._use_ssl
                )
                response.raise_for_status()
                data = response.json()
            return Task.model_validate(data["result"])
        except requests.exceptions.HTTPError:
            ...

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
            ...

    def download_file(self, response_file_id: UUID) -> list[SpeechRecognized]:
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
            return [SpeechRecognized.from_response(result) for result in results]
        except requests.exceptions.HTTPError:
            ...
