from typing import Any

from datetime import datetime
from uuid import UUID

from pydantic import PositiveInt

from modules.shared_kernel.domain import AggregateRoot, Entity

from .value_objects import Filename, FileType, Role


class Attachment(Entity):
    file_id: UUID
    filename: Filename
    format: str
    type: FileType
    size: PositiveInt
    metadata: dict[str, Any]


class Message(Entity):
    role: Role
    text: str
    attachments: list[Attachment]


class File(Entity):
    attachment_id: UUID
    filepath: str
    filesize: PositiveInt
    content: bytes
    uploaded_at: datetime


class Chat(AggregateRoot):
    type: ...
    messages_count: PositiveInt
