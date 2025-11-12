from typing import Final, Literal

AudioFormat = Literal["mp3", "wav", "ogg", "flac"]

MIME_TYPES: Final[dict[str, str]] = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "aac": "audio/aac",
    "m4a": "audio/mp4",
    "webm": "audio/webm",
    "amr": "audio/amr",
}
