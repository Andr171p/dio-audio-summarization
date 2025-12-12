import requests

from .base import BaseFoundationModel
from .models import CompletionRequest, Message, Tool


class FoundationModelClient(BaseFoundationModel):
    def completion(
            self, messages: list[Message], tools: list[Tool] | None = None
    ) -> ...:
        payload = CompletionRequest(
            modelUri=self._model_uri,
            completionOptions=self._completion_options,
            messages=messages,
            tools=tools,
        )
        try:
            with requests.Session() as session:
                response = session.post(
                    url=f"{self.base_url}/foundationModels/v1/completion",
                    headers=self._headers,
                    json=payload.model_dump(by_alias=True, exclude_none=True),
                )
                response.raise_for_status()
        except requests.exceptions.RequestException:
            ...
