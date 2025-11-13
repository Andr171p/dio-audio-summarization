from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from client.v1 import ClientV1
from config.dev import settings as dev_settings
from modules.orchestration.domain.events import ChunkPrecessedEvent
from modules.summarization.domain import SummarizationTaskCreatedEvent

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
@broker.publisher("audio_processing")
async def handle_process_audio_command(
        event: SummarizationTaskCreatedEvent, logger: Logger
) -> ChunkPrecessedEvent:
    logger.debug("Start audio processing for collection with id %s", event.collection_id)
    collection = await client.collections.get(event.collection_id)
    chunk_duration = calculate_chunk_duration(collection.total_duration, collection.record_count)
    splitter = AudioSplitter(
        chunk_duration=chunk_duration, chunk_format="wav", prefix=collection.id,
    )
    for record in collection.records:
        stream = client.collections.download_record(record.id, chunk_size=CHUNK_SIZE)
        async for chunk in splitter.split_stream(
                stream, metadata={"collection_id": collection.id, "record_id": record.id}
        ):
            yield ChunkPrecessedEvent(
                collection_id=collection.id,
                record_id=record.id,
                chunk_number=chunk.number,
                chunks_count=chunk.total_count,
                chunk_format=chunk.format,
                chunk_content=chunk.content,
                chunk_duration=chunk.duration,
                chunk_size=chunk.size,
            )
