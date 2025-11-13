# REST API клиент

## Примеры использования

```python
import asyncio
import logging
from collections.abc import AsyncIterable

import aiofiles

from client.v1 import ClientV1

client = ClientV1(base_url="http://localhost:8000")

async def main() -> None:
    # Создание коллекции
    collection = await client.collections.create(
        user_id=..., name="Untitled"
    )
    # Загрузка аудио записи
    chunk_size = 8192
    
    async def chunks_generator() -> AsyncIterable[bytes]:
        async with aiofiles.open("audio.mp3", "rb") as file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
    record = await client.collections.upload_record(
        collection_id=collection.id,
        file=chunks_generator(),
        filename="audio.mp3",
        filesize=100 * 1024,
        duration=60 * 60 * 2,
    )  


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
```