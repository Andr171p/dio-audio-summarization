from collections.abc import AsyncIterable

from ..domain import SummarizeMeetingCommand


class SummarizeMeetingUseCase:
    def __init__(self) -> None: ...

    async def execute(self, command: SummarizeMeetingCommand) -> ...:
        ...


class AttachFileUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, stream: AsyncIterable[bytes]) -> ...: ...
