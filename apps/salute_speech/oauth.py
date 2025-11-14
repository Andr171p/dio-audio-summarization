import base64
import logging
from uuid import uuid4

import requests

from .constants import SBER_DEVICES_BASE_URL
from .exceptions import AuthenticationFailedError

logger = logging.getLogger(__name__)


class OAuthSberDevicesClient:
    def __init__(
            self,
            apikey: str,
            scope: str,
            client_id: str,
            client_secret: str,
            use_ssl: bool = False,
            base_url: str = SBER_DEVICES_BASE_URL,
    ) -> None:
        self._apikey = apikey
        self._scope = scope
        self._client_id = client_id
        self._client_secret = client_secret
        self._rq_uid = uuid4()
        self._use_ssl = use_ssl
        self._base_url = base_url

    def _build_apikey(self) -> str:
        credentials = f"{self._client_id}:{self._client_secret}"
        return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    def authenticate(self) -> str:
        """Производит аутентификацию клиента, выдавая access token"""
        url = f"{self._base_url}/oauth"
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
