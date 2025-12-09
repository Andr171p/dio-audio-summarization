from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import (
    Base,
    JsonField,
    StrArray,
    StrNull,
    StrUniqueNull,
)


class BaseUserModel(Base):
    __tablename__ = "users"
    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_on": "type",
        "polymorphic_identity": "base",
        "with_polymorphic": "*",
    }

    type: Mapped[str] = mapped_column(default="base")

    username: Mapped[StrNull]
    status: Mapped[str]
    role: Mapped[str]


class AnonymousModel(BaseUserModel):
    __mapper_args__ = {"polymorphic_identity": "anonymous"}  # noqa: RUF012


class UserModel(BaseUserModel):
    __mapper_args__ = {"polymorphic_identity": "user"}  # noqa: RUF012

    email: Mapped[StrUniqueNull]
    password_hash: Mapped[StrUniqueNull]
    social_accounts: Mapped[list["SocialAccountModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    auth_methods: Mapped[StrArray]


class SocialAccountModel(Base):
    __tablename__ = "social_accounts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=False)
    provider: Mapped[str]
    social_user_id: Mapped[str]
    profile_info: Mapped[JsonField]

    user: Mapped["UserModel"] = relationship(back_populates="social_accounts")

    __table_args__ = (
        UniqueConstraint("provider", "social_user_id", name="social_account_uq"),
    )
