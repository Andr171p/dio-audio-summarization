from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from modules.shared_kernel.insrastructure.database import Base, JsonField, StrUnique


class FileMetadataModel(Base):
    __tablename__ = "file_metadata"

    filename: Mapped[str]
    filepath: Mapped[StrUnique]
    filesize: Mapped[int]
    mime_type: Mapped[str]
    type: Mapped[str]
    uploaded_at: Mapped[datetime] = mapped_column(DateTime)
    context: Mapped[JsonField]
