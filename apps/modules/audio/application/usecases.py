from collections.abc import AsyncIterable


class AttachFileUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, stream: AsyncIterable[bytes]) -> ...: ...
