from typing import Any

from collections.abc import AsyncIterable, AsyncIterator

from ..domain import AudioFormat, AudioSegment


class AudioSplitter:
    """Разбиение аудио на сегменты"""

    def __init__(
            self, segment_duration: int, segment_overlap: int, segment_format: AudioFormat,
    ) -> None:
        self._segment_duration = segment_duration
        self._segment_overlap = segment_overlap
        self._segment_format = segment_format

    async def split_stream(
            self, stream: AsyncIterable[bytes], metadata: dict[str, Any] | None = None
    ) -> AsyncIterator[AudioSegment]: ...
