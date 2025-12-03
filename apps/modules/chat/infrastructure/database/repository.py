from typing import override

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import SQLAlchemyRepository

from ...domain import Chat
from .models import ChatModel


class SQLAlchemyChatRepository(SQLAlchemyRepository[..., ...], ...):
    entity = Chat
    model = ChatModel

    @override
    async def read(self, id: UUID, **kwargs) -> Chat:
        conversation_length = kwargs.pop("conversation_length", 10)
        try:
            stmt = select(self.model).where(self.model.id == id)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__, entity_id=id
            ) from e
