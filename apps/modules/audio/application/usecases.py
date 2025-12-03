from modules.shared_kernel.application import MessageBus

from ..domain import AudioSegment, TranscriptionSegment
from .services import transcribe_audio


class TranscribeAudioUseCase:
    def __init__(self, message_bus: MessageBus) -> None:
        self._message_bus = message_bus

    async def execute(self, audio_segment: AudioSegment) -> ...:
        text = await transcribe_audio(audio_segment.content)
        transcription_segment = TranscriptionSegment.from_audio(text, audio_segment)
