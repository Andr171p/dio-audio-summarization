from sqlalchemy.orm import Mapped

from modules.shared_kernel.insrastructure.database import (
    Base,
    StrText,
    StrUnique,
    UUIDField,
    UUIDFieldNull,
)


class SummarizationTaskModel(Base):
    __tablename__ = "summarization_tasks"

    collection_id: Mapped[UUIDField]
    summary_type: Mapped[str]
    document_format: Mapped[str]
    status: Mapped[str]
    waiting_time: Mapped[int]
    summary_id: Mapped[UUIDFieldNull]


class TranscriptionModel(Base):
    __tablename__ = "transcriptions"

    record_id: Mapped[UUIDField]
    segment_id: Mapped[int]
    segment_duration: Mapped[int]
    text: Mapped[StrText]


class SummaryTemplateModel(Base):
    __tablename__ = "summary_templates"

    user_id: Mapped[UUIDField]
    filepath: Mapped[StrUnique]
    md_text: Mapped[StrText]
