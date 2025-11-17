from dishka.integrations.faststream import FromDishka as Depends
from faststream import Logger
from faststream.rabbit import RabbitRouter

from ...application import (
    AudioSplitEventHandler,
    AudioTranscribedEventHandler,
    SoundEnhancedEventHandler,
    TranscriptionSummarizedEventHandler,
)
from ...domain import (
    AudioSplitEvent,
    AudioTranscribedEvent,
    SoundEnhancedEvent,
    SummarizeTranscriptionCommand,
    TranscriptionSummarizedEvent,
)

router = RabbitRouter()


@router.subscriber("audio_splitting")
async def handle_audio_split_event(
        event: AudioSplitEvent,
        handler: Depends[AudioSplitEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)


@router.subscriber("sound_enhancement")
async def handle_sound_enhanced_event(
        event: SoundEnhancedEvent,
        handler: Depends[SoundEnhancedEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)


@router.subscriber("transcribing")
@router.publisher("summarizing")
async def handle_audio_transcribed_event(
        event: AudioTranscribedEvent,
        handler: Depends[AudioTranscribedEventHandler],
) -> SummarizeTranscriptionCommand | None:
    return await handler.handle(event)


@router.subscriber("summarizing")
async def handle_transcription_summarized_event(
        event: TranscriptionSummarizedEvent,
        handler: Depends[TranscriptionSummarizedEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)
