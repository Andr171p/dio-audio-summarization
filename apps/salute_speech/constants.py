from typing import Any, Final, Literal

# Язык для распознавания речи
Language = Literal["ru-RU", "en-US", "kk-KZ", "ky-KG", "uz-UZ"]
# Допустимые кодировки аудио
AudioEncoding = Literal["PCM_S16LE", "OPUS", "MP3", "FLAC", "ALAW", "MULAW", "G729"]
# Конфигурации для допустимых аудио кодировок
AUDIO_ENCODING_CONFIG: Final[dict[AudioEncoding, dict[str, Any]]] = {
    "PCM_S16LE": {
        "max_channels": 8,
        "samplerate_range": (8000, 96000),
        "requires_samplerate": False,  # При наличии WAV заголовка,
        "content_type": "audio/x-pcm;bit=16;rate={samplerate}"
    },
    "OPUS": {
        "max_channels": 1,
        "samplerate_range": None,  # Определяется автоматически
        "requires_samplerate": False,
        "content_type": "audio/ogg;codecs=opus"
    },
    "MP3": {
        "max_channels": 2,
        "samplerate_range": None,
        "requires_samplerate": False,
        "content_type": "audio/mpeg"
    },
    "FLAC": {
        "max_channels": 8,
        "samplerate_range": None,
        "requires_samplerate": False,
        "content_type": "audio/flac"
    },
    "ALAW": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),  # Фиксированная 8 кГц
        "requires_samplerate": True,  # Если нет заголовка WAV
        "content_type": "audio/pcma;rate={samplerate}"
    },
    "MULAW": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),
        "requires_samplerate": True,
        "content_type": "audio/pcmu;rate={samplerate}"
    },
    "G729": {
        "max_channels": 1,
        "samplerate_range": (8000, 8000),
        "requires_samplerate": False,
        "content_type": "audio/g729"
    }
}
