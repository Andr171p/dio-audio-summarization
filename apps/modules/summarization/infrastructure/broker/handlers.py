from dishka.integrations.faststream import FromDishka as Depends
from faststream import Logger
from faststream.rabbit import RabbitQueue, RabbitRouter

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

audio_splitting_queue = RabbitQueue(name="audio_splitting", durable=True)
sound_enhancement_queue = RabbitQueue(name="sound_enhancement", durable=True)
transcribing_queue = RabbitQueue(name="transcribing", durable=True)
summarizing_queue = RabbitQueue(name="summarizing", durable=True)


@router.subscriber(audio_splitting_queue)
async def handle_audio_split_event(
        event: AudioSplitEvent,
        handler: Depends[AudioSplitEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)


@router.subscriber(sound_enhancement_queue)
async def handle_sound_enhanced_event(
        event: SoundEnhancedEvent,
        handler: Depends[SoundEnhancedEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)


@router.subscriber(transcribing_queue)
@router.publisher(summarizing_queue)
async def handle_audio_transcribed_event(
        event: AudioTranscribedEvent,
        handler: Depends[AudioTranscribedEventHandler],
) -> SummarizeTranscriptionCommand | None:
    return await handler.handle(event)


@router.subscriber(summarizing_queue)
async def handle_transcription_summarized_event(
        event: TranscriptionSummarizedEvent,
        handler: Depends[TranscriptionSummarizedEventHandler],
        logger: Logger
) -> ...:
    await handler.handle(event)
