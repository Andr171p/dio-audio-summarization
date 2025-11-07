from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.audio.domain.events import AudioCollectionSummarizationStartedEvent

import asyncio

from modules.shared_kernel.application import Storage

from ..domain.commands import SplitAudioRecordsCommand

AUDIO_SEGMENT_DURATION = 20 * 60  # 20 минут


class AudioCollectionSummarizationStartedHandler:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    async def handle(
            self, event: "AudioCollectionSummarizationStartedEvent"
    ) -> SplitAudioRecordsCommand:
        presigned_urls: list[str] = await asyncio.gather(
            *[
                self.storage.generate_presigned_url(record_filepath)
                for record_filepath in event.record_filepaths]
        )
        return SplitAudioRecordsCommand(
            collection_id=event.collection_id,
            record_presigned_urls=presigned_urls,
            collection_duration=event.collection_duration,
            segment_duration=AUDIO_SEGMENT_DURATION
        )
