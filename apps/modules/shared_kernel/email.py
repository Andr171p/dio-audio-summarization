from pydantic import EmailStr, Field

from .domain import ValueObject


class LetterAttachment(ValueObject):
    content: bytes
    filename: str
    content_type: str


class EmailLetter(ValueObject):
    subject: str
    sender_email: EmailStr
    recipient_emails: list[EmailStr]
    html_body: str
    cc: list[EmailStr] = Field(default_factory=list)
    bcc: list[EmailStr] = Field(default_factory=list)
    reply_to: EmailStr | None = None
    attachments: list[LetterAttachment] = Field(default_factory=list)
