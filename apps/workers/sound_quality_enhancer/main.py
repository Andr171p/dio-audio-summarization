import io
import logging

import soundfile as sf
from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker
from pedalboard import Compressor, Gain, LowShelfFilter, NoiseGate, Pedalboard

from config.dev import settings as dev_settings
from modules.shared_kernel.audio import AudioFormat, AudioSegment
from modules.summarization.domain import SoundQualityEnhancedEvent

logger = logging.getLogger(__name__)

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)


def enhance_sound_quality(content: bytes, output_format: str = "wav") -> tuple[bytes, int]:
    """Улучшение качества звука используя технологии Spotify.

    :param content: Байты аудио записи.
    :param output_format: Формат аудио на выходе, после обработки (по умолчанию WAV).
    :returns: Байты обработанной аудио записи + частота дискретизации.
    """
    with io.BytesIO(content) as stream:
        content, samplerate = sf.read(stream)
    board = Pedalboard([
        NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
        Compressor(threshold_db=-16, ratio=4, attack_ms=5, release_ms=100),
        LowShelfFilter(cutoff_frequency_hz=400, gain_db=8, q=1),
        Gain(gain_db=2)
    ])
    effected = board(content, samplerate)
    with io.BytesIO(effected) as stream:
        sf.write(stream, content, samplerate, format=output_format)
        stream.seek(0)
        return stream.read(), samplerate


@broker.subscriber("sound_quality_enhancement")
@broker.publisher("sound_quality_enhancement")
async def handle_sound_quality_enhancement(
        audio_segment: AudioSegment, logger: Logger
) -> AudioSegment:
    logger.info(
        "Start sound quality enhancement for audio segment %s/%s with duration %s sec",
        audio_segment.id, audio_segment.total_count, audio_segment.duration,
        extra=audio_segment.metadata
    )
    enhanced_sound, samplerate = enhance_sound_quality(audio_segment.content)
    logger.info(
        "Finished sound quality enhancement for audio segment %s/%s with duration %s sec",
        audio_segment.id, audio_segment.total_count, audio_segment.duration,
        extra=audio_segment.metadata
    )
    if audio_segment.is_last:
        event = SoundQualityEnhancedEvent(collection_id=audio_segment.metadata["collection_id"])
        await broker.publish(event, queue="sound_quality_enhancement")
    return AudioSegment(
        id=audio_segment.id,
        total_count=audio_segment.total_count,
        content=enhanced_sound,
        format=AudioFormat.WAV,
        size=len(enhanced_sound),
        duration=audio_segment.duration,
        samplerate=samplerate,
        channels=audio_segment.channels,
        metadata=audio_segment.metadata
    )
