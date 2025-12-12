from pydantic import EmailStr, Field

from modules.shared_kernel.domain import ValueObject


class LetterAttachment(ValueObject):
    """Медиа вложения для отправки письма.

    Attributes:
        content: Байтовый контент файла.
        filename: Имя файла, которое увидит получатель.
        content_type: MIME-тип содержимого (например, 'application/pdf', 'image/png').
    """

    content: bytes
    filename: str
    content_type: str


class EmailLetter(ValueObject):
    """Письмо для отправки

    Attributes:
        subject: Тема письма.
        sender_email: Email отправителя.
        recipient_emails: Список email адресов получателей.
        body_markup: Тело письма в HTML формате.
        cc: Список email адресов для копии письма (carbon copy).
        bcc: Список email адресов для скрытой копии (blind carbon copy).
        reply_to: Email для отправки ответа (если отличается от sender_email).
        attachments: Список вложений к письму.
    """

    subject: str
    sender_email: EmailStr
    recipient_emails: list[EmailStr]
    body_markup: str
    cc: list[EmailStr] = Field(default_factory=list)
    bcc: list[EmailStr] = Field(default_factory=list)
    reply_to: EmailStr | None = None
    attachments: list[LetterAttachment] = Field(default_factory=list)
