import time
import logging
from pathlib import Path

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Request, status
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "uploaded_files"

logger = logging.getLogger(__name__)

app = FastAPI(title="File Loading Benchmark 📁")


class FileInfo(BaseModel):
    filename: str
    filepath: str
    filesize: float
    loading_time: float


@app.post(path="files/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(uploaded_file: UploadFile = File(...)) -> FileInfo:
    start_time = time.perf_counter()
    content = await uploaded_file.read()
    filepath = FILES_DIR / uploaded_file.filename
    async with aiofiles.open(filepath, mode="wb") as file:
        await file.write(content)
    loading_time = time.perf_counter() - start_time
    return FileInfo(
        filename=uploaded_file.filename,
        filepath=str(filepath),
        filesize=round(len(content) / (1024 * 1024), 3),
        loading_time=round(loading_time, 3),
    )


@app.post(path="/files/upload-stream", status_code=status.HTTP_201_CREATED)
async def upload_file_stream(
        request: Request,
        filename: str = Form(..., description="File name"),
) -> FileInfo:
    start_time = time.perf_counter()
    filepath = FILES_DIR / filename
    filesize = 0
    async with aiofiles.open(filepath, mode="wb") as file:
        async for chunk in request.stream():
            await file.write(chunk)
            filesize += len(chunk)
    loading_time = time.perf_counter() - start_time
    return FileInfo(
        filename=filename,
        filepath=str(filepath),
        filesize=round(filesize / (1024 * 1024), 3),
        loading_time=round(loading_time, 3),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
