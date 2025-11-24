from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import Base, JsonField, StrArray, StrUniqueNull


class UserModel(Base):
    __tablename__ = "users"

    email: Mapped[StrUniqueNull]
    username: Mapped[StrUniqueNull]
    password_hash: Mapped[StrUniqueNull]
    status: Mapped[str]
    role: Mapped[str]
    social_accounts: Mapped[list["SocialAccountModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    auth_providers: Mapped[StrArray]


class SocialAccountModel(Base):
    __tablename__ = "social_accounts"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=False)
    provider: Mapped[str]
    profile_info: Mapped[JsonField]

    user: Mapped["UserModel"] = relationship(back_populates="social_accounts")
