from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.audio.infrastructure.container import AudioProvider
from modules.shared_kernel.insrastructure.container import SharedKernelProvider
from modules.summarization.infrastructure.container import SummarizationProvider

container: Final[AsyncContainer] = make_async_container(
    SharedKernelProvider(), AudioProvider(), SummarizationProvider(),
)
