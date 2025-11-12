from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker

from client import ClientV1
from config.dev import settings as dev_settings
from modules.orchestration.domain.commands import ProcessAudioCommand
from modules.orchestration.domain.events import ChunkPrecessedEvent

from .splitter import AudioSplitter

broker = RabbitBroker(url=dev_settings.rabbitmq.url)

app = FastStream(broker)

client = ClientV1(base_url=...)


def should_chunking(collection_duration: int) -> bool:
    return collection_duration > ...


def calculate_chunk_duration(collection_duration: int, record_count: int) -> int:
    ...


@broker.subscriber("audio_processing")
@broker.publisher("audio_processing")
async def handle_process_audio_command(
        command: ProcessAudioCommand, logger: Logger
) -> ChunkPrecessedEvent:
    collection = await client.collections.get(command.collection_id)
    collection_duration = sum(record.metadata.duration for record in collection.records)
    splitter = AudioSplitter(
        chunk_duration=..., chunk_format="wav", prefix="",
    )
    for record in collection.records:
        stream = client.collections.download_record(record.id, chunk_size=8192)
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
