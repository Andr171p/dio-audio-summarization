from ..domain import SummarizeMeetingCommand


class SummarizeMeetingCommandHandler:
    def __init__(self) -> None: ...

    async def handle(self, command: SummarizeMeetingCommand) -> ...: ...
