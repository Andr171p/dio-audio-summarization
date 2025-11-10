from faststream import Logger
from faststream.rabbit import RabbitRouter

from ...domain.commands import EnhanceSoundQualityCommand
from ...domain.events import AudioPrecessedEvent

router = RabbitRouter()


@router.subscriber("audio_processing")
@router.publisher("sound_quality_enhancement")
async def handle_processed_audio(
        event: AudioPrecessedEvent, logger: Logger
) -> EnhanceSoundQualityCommand:
    ...
