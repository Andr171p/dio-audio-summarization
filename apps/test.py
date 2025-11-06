import asyncio
from pathlib import Path
from uuid import UUID

import aiohttp


async def upload_large_audio_file(
        collection_id: UUID,
        file_path: str,
        base_url: str = "http://localhost:8000",
        chunk_size: int = 8 * 1024 * 1024  # 8MB chunks
) -> None:
    """Потоковая загрузка больших аудио файлов в коллекцию"""

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")

    file_size = file_path.stat().st_size
    print(file_size)

    # Заголовки согласно AudioMetadataHeaders
    headers = {
        "filename": file_path.name,
        "filesize": str(file_size),
        "duration": "120",
        "channels": "2",
        "samplerate": "44100",
        "bitrate": "320",
    }

    async with aiohttp.ClientSession() as session:
        # Асинхронный генератор для потоковой отправки
        async def file_sender():
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        url = f"{base_url}/api/v1/collections/{collection_id}/records/upload"
        try:
            async with session.post(
                    url,
                    data=file_sender(),
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour timeout для больших файлов
            ) as response:
                if response.status == 202:
                    result = await response.json()
                    print(f"✅ Upload successful: {result}")
                    return result
                error_text = await response.text()
                print(f"❌ Upload failed: {response.status} - {error_text}")
                response.raise_for_status()

        except aiohttp.ClientError as e:
            print(f"❌ Network error during upload: {e}")
            raise
    return None


# Использование
async def main():
    collection_id = UUID("8b1d84c4-7ed8-4a11-a751-0eb60c420cc9")

    # Для больших файлов используем потоковую загрузку
    await upload_large_audio_file(collection_id, "29.10.2025 11.07.m4a")


if __name__ == "__main__":
    asyncio.run(main())
