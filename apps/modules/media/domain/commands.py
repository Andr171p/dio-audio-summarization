from pydantic import PositiveInt

from modules.shared_kernel.domain import Command

from .primitives import Filename, MimeType


class UploadFileCommand(Command):
    filename: Filename
    mime_type: MimeType
    filesize: PositiveInt
    tenant: str
    entity_type: str
    entity_id: str
