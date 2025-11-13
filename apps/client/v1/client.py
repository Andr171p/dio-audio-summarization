from .resources import CollectionsResource


class ClientV1:
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self._base_url = base_url
        self._timeout = timeout

    @property
    def collections(self) -> CollectionsResource:
        return CollectionsResource(f"{self._base_url}/collections")
