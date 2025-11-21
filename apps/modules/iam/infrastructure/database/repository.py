from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from modules.shared_kernel.application.exceptions import ConflictError, CreationError, ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import UserRepository
from ...domain import User
from .models import UserModel


class UserDataMapper(DataMapper[User, UserModel]):
    def model_to_entity(self, model: UserModel) -> User: ...

    def entity_to_model(self, entity: User) -> UserModel: ...


class SQLAlchemyUserRepository(UserRepository, SQLAlchemyRepository[User, UserModel]):
    entity = User
    model = UserModel
    data_mapper = UserDataMapper

    async def get_by_email(self, email: EmailStr) -> User | None:
        try:
            stmt = select(self.model).where(self.model.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__, entity_id=email, original_error=e
            ) from e
