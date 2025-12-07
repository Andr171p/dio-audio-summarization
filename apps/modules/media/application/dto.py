from fastapi import Header
from pydantic import PositiveInt

from modules.shared_kernel.application import DTO


class FileHeaders(DTO):
    filename: str = Header(..., description="Имя файла пользователя")
    mime_type: str = Header(..., description="MIME-тип файла")
    filesize: PositiveInt = Header(..., description="Размер файла в байтах")
    tenant: str = Header()
    entity_type: str = Header()
    entity_id: str = Header()
