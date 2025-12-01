from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.shared_kernel.insrastructure.database import Base, JsonField, TextNull, UUIDField


class AttachmentModel(Base):
    __tablename__ = "attachments"

    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"), unique=False)
    file_id: Mapped[UUIDField]
    filename: Mapped[str]
    format: Mapped[str]
    type: Mapped[str]
    size: Mapped[int]
    metadata: Mapped[JsonField]

    message: Mapped["MessageModel"] = relationship(back_populates="attachments")


class MessageModel(Base):
    __tablename__ = "messages"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"), unique=False)
    role: Mapped[str]
    text: Mapped[TextNull]
    attachments: Mapped[list["AttachmentModel"]] = relationship(back_populates="message")
    metadata: Mapped[JsonField]

    chat: Mapped["ChatModel"] = relationship(back_populates="messages")


class ChatModel(Base):
    __tablename__ = "chats"

    user_id: Mapped[UUIDField]
    title: Mapped[str]
    messages: Mapped[list["MessageModel"]] = relationship(back_populates="chat")
