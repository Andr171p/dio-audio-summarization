from typing import TypedDict

import math
from pathlib import Path

import mutagen

from ..domain import UnsupportedAudioError


class AudioInfo(TypedDict):
    """Информация об аудио файле"""

    duration: int
    samplerate: int
    channels: int
    bitrate: int


def extract_audio_info(filepath: Path) -> AudioInfo:
    """Получение информации об аудио"""

    audio = mutagen.File(filepath, easy=True)
    if audio is None:
        raise UnsupportedAudioError(f"Audio file is not supported or damaged: {filepath}")
    return {
        "duration": math.floor(audio.info.length),
        "samplerate": audio.info.sample_rate,
        "channels": audio.info.channels,
        "bitrate": audio.info.bitrate,
    }
