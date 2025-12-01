from ..domain import SummarizeAudioCommand


class SummarizeAudioCommandHandler:
    def __init__(self) -> None: ...

    async def handle(self, command: SummarizeAudioCommand) -> ...: ...
