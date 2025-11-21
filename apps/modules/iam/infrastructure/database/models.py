from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    JsonField,
    JsonFieldNullable,
    StringArray,
    StrUnique,
    StrUniqueNullable,
)


class UserModel(Base):
    __tablename__ = "users"

    email: Mapped[StrUniqueNullable]
    username: Mapped[StrUniqueNullable]

    credentials: Mapped[JsonFieldNullable]
    social_accounts: Mapped[list["SocialAccountModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    auth_providers: Mapped[StringArray]


class UserCredentialsModel(Base):
    __tablename__ = "user_credentials"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    email: Mapped[StrUnique]
    password_hash: Mapped[StrUnique]

    user: Mapped["UserModel"] = relationship(back_populates="credentials")


class SocialAccountModel(Base):
    __tablename__ = "social_accounts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=False)
    provider: Mapped[str]
    profile_data: Mapped[JsonField]

    user: Mapped["UserModel"] = relationship(back_populates="social_accounts")
