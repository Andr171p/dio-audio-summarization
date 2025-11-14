from collections.abc import AsyncIterable

from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from client.v1 import ClientV1
from config.dev import settings as dev_settings
from modules.shared_kernel.audio import AudioFormat, AudioSegment
from modules.summarization.domain import AudioProcessedEvent, SummarizationTaskCreatedEvent

from .splitter import AudioSplitter

CHUNK_SIZE = 8192  # Размер чанка для скачивания аудио записей

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = ClientV1(base_url=dev_settings.app.url)


def should_chunking(total_duration: int) -> bool:
    return total_duration > ...


def calculate_chunk_duration(total_duration: int, record_count: int) -> int:
    ...


@broker.subscriber("audio_processing")
@broker.publisher("sound_quality_enhancement")
async def handle_process_audio_command(
        event: SummarizationTaskCreatedEvent, logger: Logger
) -> AsyncIterable[AudioSegment]:
    logger.debug("Start audio processing for collection with id %s", event.collection_id)
    collection = await client.collections.get(event.collection_id)
    chunk_duration = calculate_chunk_duration(collection.total_duration, collection.record_count)
    splitter = AudioSplitter(
        chunk_duration=chunk_duration, chunk_format=AudioFormat.WAV, prefix=collection.id,
    )
    segments_count = 0
    for record in collection.records:
        stream = client.collections.download_record(record.id, chunk_size=CHUNK_SIZE)
        async for audio_segment in splitter.split_stream(
                stream, metadata={"collection_id": collection.id, "record_id": record.id}
        ):
            yield audio_segment
            segments_count += 1
    event = AudioProcessedEvent(collection_id=collection.id, segments_count=segments_count)
    await broker.publish(event, queue="audio_processing")
