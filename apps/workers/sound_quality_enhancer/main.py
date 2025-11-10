import io
import logging

import soundfile as sf
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pedalboard import Compressor, Gain, LowShelfFilter, NoiseGate, Pedalboard

from config.dev import settings as dev_settings
from modules.orchestration.domain.commands import EnhanceSoundQualityCommand
from modules.orchestration.domain.events import SoundQualityEnhancedEvent

logger = logging.getLogger(__name__)

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)


def enhance_sound_quality(content: bytes, output_format: str = "wav") -> tuple[bytes, int]:
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
def handle_sound_quality_enhancement(
        command: EnhanceSoundQualityCommand
) -> SoundQualityEnhancedEvent:
    enhanced_sound, samplerate = enhance_sound_quality(
        content=command.chunk_content, output_format=command.output_format
    )
    return SoundQualityEnhancedEvent(
        collection_id=command.collection_id,
        record_id=command.record_id,
        chunk_number=command.chunk_number,
        chunk_content=enhanced_sound,
        audio_format=command.output_format,
        samplerate=samplerate
    )
