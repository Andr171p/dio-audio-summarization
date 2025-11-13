from typing import Any

NOT_FOUND_STATUS = 404


class ClientError(Exception):
    def __init__(
            self, message: str, status_code: int, response_data: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NotFoundError(ClientError):
    pass
