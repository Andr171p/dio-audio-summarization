from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.audio.infrastructure.container import AudioProvider
from modules.shared_kernel.insrastructure.container import SharedProvider

container: Final[AsyncContainer] = make_async_container(
    SharedProvider(), AudioProvider()
)
