import io

import soundfile as sf
from pedalboard import Compressor, Gain, LowShelfFilter, NoiseGate, Pedalboard

from modules.shared_kernel.audio import AudioFormat


def enhance_sound_quality(audio: bytes, output_format: AudioFormat = "wav") -> tuple[bytes, int]:
    """Улучшение качества звука используя технологии Spotify.

    :param audio: Байты аудио записи.
    :param output_format: Формат аудио на выходе, после обработки (по умолчанию WAV).
    :returns: Байты обработанной аудио записи + частота дискретизации.
    """
    with io.BytesIO(audio) as stream:
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
