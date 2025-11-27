from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import UserRepository
from ...domain import AuthProvider, User
from .models import SocialAccountModel, UserModel


class UserDataMapper(DataMapper[User, UserModel]):
    @classmethod
    def model_to_entity(cls, model: UserModel) -> User:
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

    @classmethod
    def entity_to_model(cls, entity: User) -> UserModel:
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
                    social_user_id=social_account.social_user_id,
                    profile_info=social_account.profile_info,
                )
                for social_account in entity.social_accounts
            ],
            auth_providers=entity.auth_providers,
        )


class SQLAlchemyUserRepository(SQLAlchemyRepository[User, UserModel], UserRepository):
    entity = User
    model = UserModel
    data_mapper = UserDataMapper

    async def get_by_email(self, email: EmailStr) -> User | None:
        try:
            stmt = select(self.model).where(self.model.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return None if model is None else self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__, entity_id=email, original_error=e
            ) from e

    async def get_by_social_account(
            self, provider: AuthProvider, social_user_id: str
    ) -> User | None:
        try:
            stmt = (
                select(self.model)
                .join(SocialAccountModel)
                .where(
                    (SocialAccountModel.provider == provider) &
                    (SocialAccountModel.social_user_id == social_user_id)
                )
                .options(joinedload(self.model.social_accounts))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return None if model is None else self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__, entity_id=social_user_id, original_error=e
            ) from e
