from sqlalchemy.orm import Mapped

from modules.shared_kernel.insrastructure.database import Base


class SummarizationTaskModel(Base):
    __tablename__ = "summarization_tasks"

    status: Mapped[str]
    waiting_time: Mapped[int]
