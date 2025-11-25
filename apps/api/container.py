from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.audio.infrastructure.container import AudioProvider
from modules.iam.infrastructure.container import IAMProvider
from modules.shared_kernel.insrastructure.container import SharedKernelProvider

container: Final[AsyncContainer] = make_async_container(
    SharedKernelProvider(), AudioProvider(), IAMProvider()
)
