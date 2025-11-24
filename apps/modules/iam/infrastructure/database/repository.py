from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import UserRepository
from ...domain import User
from .models import SocialAccountModel, UserModel


class UserDataMapper(DataMapper[User, UserModel]):
    def model_to_entity(self, model: UserModel) -> User:  # noqa: PLR6301
        return User.model_validate({
            "id": model.id,
            "username": model.username,
            "email": model.email,
            "password_hash": model.password_hash,
            "status": model.status,
            "role": model.role,
            "social_accounts": model.social_accounts,
            "auth_providers": model.auth_providers,
        })

    def entity_to_model(self, entity: User) -> UserModel:  # noqa: PLR6301
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
            status=entity.status,
            role=entity.role,
            social_accounts=[
                SocialAccountModel(
                    provider=social_account.provider,
                    user_id=social_account.user_id,
                    profile_info=social_account.profile_info,
                )
                for social_account in entity.social_accounts
            ],
            auth_providers=entity.auth_providers,
        )


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
