from typing import TypeVar

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import UserRepository
from ...domain import AnyUser, AuthProvider, Guest, User
from .models import BaseUserModel, GuestModel, SocialAccountModel, UserModel

AnyUserModel = TypeVar("AnyUserModel", bound=UserModel | GuestModel)


class UserDataMapper(DataMapper[AnyUser, AnyUserModel]):
    @classmethod
    def model_to_entity(cls, model: AnyUserModel) -> AnyUser:
        if isinstance(model, UserModel):
            return User.model_validate({
                "id": model.id,
                "username": model.username,
                "email": model.email,
                "password_hash": model.password_hash,
                "status": model.status,
                "role": model.role,
                "social_accounts": model.social_accounts,
                "auth_methods": model.auth_methods,
                "created_at": model.created_at,
            })
        return Guest.model_validate({
            "id": model.id,
            "device_id": model.device_id,
            "expires_at": model.expires_at,
            "username": model.username,
            "status": model.status,
            "role": model.role,
            "created_at": model.created_at,
        })

    @classmethod
    def entity_to_model(cls, entity: AnyUser) -> AnyUserModel:
        if isinstance(entity, User):
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
                auth_methods=entity.auth_methods,
                created_at=entity.created_at,
            )
        return GuestModel(
            id=entity.id,
            device_id=entity.device_id,
            expires_at=entity.expires_at,
            username=entity.username,
            status=entity.status,
            role=entity.role,
            created_at=entity.created_at,
        )


class SQLAlchemyUserRepository(SQLAlchemyRepository[AnyUser, AnyUserModel], UserRepository):
    entity = User
    model = BaseUserModel
    data_mapper = UserDataMapper

    async def get_by_device_id(self, device_id: str) -> Guest | None:
        try:
            stmt = select(GuestModel).where(GuestModel.device_id == device_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return None if model is None else self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__, entity_id=device_id, original_error=e
            ) from e

    async def get_by_email(self, email: EmailStr) -> User | None:
        try:
            stmt = select(UserModel).where(UserModel.email == email)
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
                select(UserModel)
                .join(SocialAccountModel)
                .where(
                    (SocialAccountModel.provider == provider) &
                    (SocialAccountModel.social_user_id == social_user_id)
                )
                .options(joinedload(UserModel.social_accounts))
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return None if model is None else self.data_mapper.model_to_entity(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__name__, entity_id=social_user_id, original_error=e
            ) from e
