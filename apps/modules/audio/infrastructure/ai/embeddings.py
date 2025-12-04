import logging

import aiohttp
import requests
from langchain_core.embeddings import Embeddings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class RemoteHTTPEmbeddings(Embeddings):
    """Совместимый с LangChain клиент для взаимодействия с моделью ембедингов на HTTP сервере"""

    def __init__(
            self,
            base_url: str,
            normalize: bool = False,
            batch_size: int = 32,
            timeout: int = 60,
            max_retries: int = 5,
    ) -> None:
        self._base_url = base_url
        self._normalize = normalize
        self.batch_size = batch_size
        self.timeout = timeout
        self.retries = Retry(total=max_retries)

    def wait_for_healthy(self) -> bool:
        """Ожидает и проверяет доступность сервера.

        :return True если сервер готов к работе,
        False предыдущие попытки были неудачны.
        """

        url = f"{self._base_url}/health"
        try:
            with requests.Session() as session:
                session.mount(url, HTTPAdapter(max_retries=self.retries))
                response = session.get(url=url, timeout=self.timeout)
                data = response.json()
            if data["status"] != "ok":
                logger.info("Service status is %s", data["status"])
                return False
        except TimeoutError:
            logger.exception("Service still not healthy! Error: {e}")
            return False
        else:
            logger.info("Service healthy!", extra=data)
            return True

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        with requests.Session() as session:
            response = session.post(
                url=f"{self._base_url}/api/v1/embeddings",
                headers={"Content-Type": "application/json"},
                json={"texts": texts, "normalize": self._normalize},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def _aget_embeddings(self, texts: list[str]) -> list[list[float]]:
        async with aiohttp.ClientSession(
            base_url=self._base_url, timeout=aiohttp.ClientTimeout(self.timeout)
        ) as session, session.post(
            url="/api/v1/embeddings/vectorize",
            headers={"Content-Type": "application/json"},
            json={"texts": texts, "normalize": self._normalize},
        ) as response:
            response.raise_for_status()
            return await response.json()

    def embed_query(self, text: str) -> list[float]:
        return self._get_embeddings([text])[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._get_embeddings(texts)

    async def aembed_query(self, text: str) -> list[float]:
        embeddings = await self._aget_embeddings([text])
        return embeddings[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._aget_embeddings(texts)
