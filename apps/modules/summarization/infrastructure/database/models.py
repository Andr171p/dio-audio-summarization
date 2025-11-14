from sqlalchemy.orm import Mapped

from modules.shared_kernel.insrastructure.database import (
    Base,
    PostgresUUID,
    PostgresUUIDNullable,
    StrText,
    StrUnique,
)


class SummarizationTaskModel(Base):
    __tablename__ = "summarization_tasks"

    status: Mapped[str]
    waiting_time: Mapped[int]
    summary_id: Mapped[PostgresUUIDNullable]


class TranscriptionModel(Base):
    __tablename__ = "transcriptions"

    record_id: Mapped[PostgresUUID]
    segment_id: Mapped[int]
    segment_duration: Mapped[int]
    text: Mapped[StrText]


class SummaryTemplateModel(Base):
    __tablename__ = "summary_templates"

    user_id: Mapped[PostgresUUID]
    filepath: Mapped[StrUnique]
    md_text: Mapped[StrText]
