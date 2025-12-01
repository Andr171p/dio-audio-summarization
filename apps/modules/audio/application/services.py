from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.media.application import FileMetaRepository, Storage
    from modules.media.domain import Filepath

import logging
import os
from pathlib import Path

import aiofiles

from modules.shared_kernel.application.exceptions import NotFoundError

from ..domain.entities import Audio
from ..utils.audio import get_audio_info

logger = logging.getLogger(__name__)


class AudioMetaExtractor:
    def __init__(
            self,
            file_meta_repository: "FileMetaRepository",
            storage: "Storage",
            temp_dir: Path
    ) -> None:
        self._file_meta_repository = file_meta_repository
        self._storage = storage
        self._temp_dir = temp_dir

    async def extract(self, filepath: Filepath, part_size: int) -> Audio:
        filemeta = await self._file_meta_repository.get_by_filepath(filepath)
        if filemeta is None:
            raise NotFoundError(f"File {filepath} not found!", entity_name="FileMetadata")
        try:
            logger.info("Start scan file %s", filepath)
            async with aiofiles.tempfile.NamedTemporaryFile(
                mode="w",
                suffix=f".{filemeta.extension}",
                prefix="audio_scanning",
                dir=self._temp_dir,
                delete=False,
            ) as temp_file:
                async for file_part in self._storage.download_multipart(
                        filemeta.filepath, part_size=part_size
                ):
                    await temp_file.write(file_part.content)
                audioinfo = get_audio_info(Path(temp_file.name))
            return Audio(
                file_id=filemeta.id,
                format=filemeta.extension,
                duration=audioinfo["duration"],
                channels=audioinfo["channels"],
                sample_rate=audioinfo["samplerate"],
                metadata={"filepath": filemeta.filepath},
            )
        except OSError:
            logger.exception(
                "Error occurred while extract audio metadata of file %s, error message: {e}",
                filepath
            )
        finally:
            os.unlink(temp_file.name)
            logger.info("Temp file %s deleted", filepath)
