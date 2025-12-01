from typing import Any

import os
from enum import StrEnum
from pathlib import Path

from pydantic import Field, PositiveInt

from modules.shared_kernel.domain import ValueObject


class AudioFormat(StrEnum):
    """Допустимые аудио форматы"""

    # Основные форматы
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    WMA = "wma"
    AIFF = "aiff"
    # Форматы высокого качества
    ALAC = "alac"
    DSF = "dsf"
    DFF = "dff"
    # Специализированные форматы
    OPUS = "opus"
    AMR = "amr"
    RA = "ra"
    MID = "mid"
    MIDI = "midi"
    # Форматы для потоковой передачи
    M3U = "m3u"
    M3U8 = "m3u8"
    PLS = "pls"
    # Контейнерные форматы
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    WEBM = "webm"

    @classmethod
    def from_filepath(cls, filepath: str | Path | os.PathLike[str]) -> "AudioFormat":
        return cls(Path(filepath).suffix.replace(".", ""))

    @classmethod
    def lossless_formats(cls) -> list["AudioFormat"]:
        """Форматы без потерь качества"""
        return [cls.FLAC, cls.WAV, cls.AIFF, cls.ALAC, cls.DSF, cls.DFF]

    @classmethod
    def lossy_formats(cls) -> list["AudioFormat"]:
        """Форматы с потерями качества"""
        return [cls.MP3, cls.AAC, cls.OGG, cls.WMA, cls.OPUS, cls.M4A]

    @classmethod
    def streaming_formats(cls) -> list["AudioFormat"]:
        """Форматы для потоковой передачи"""
        return [cls.M3U, cls.M3U8, cls.PLS]

    @classmethod
    def container_formats(cls) -> list["AudioFormat"]:
        """Контейнерные форматы"""
        return [cls.MP4, cls.AVI, cls.MKV, cls.WEBM]

    def is_lossless(self) -> bool:
        """Является ли формат, форматом без потерь"""
        return self in self.lossless_formats()


class AudioSegment(ValueObject):
    number: PositiveInt
    total_count: PositiveInt
    content: bytes
    format: AudioFormat
    size: PositiveInt
    duration: PositiveInt
    channels: PositiveInt | None = None
    samplerate: PositiveInt | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_last(self) -> bool:
        """Является ли сегмент последним в последовательности"""

        return self.number == self.total_count
