import logging
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from ...application import EmailSender, EmailSendingError
from ...domain import EmailLetter

logger = logging.getLogger(__name__)


class SMTPEmailSender(EmailSender):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        timeout: int = 30,
    ) -> None:
        self._username = username
        self._password = password
        self._smtp_config = {
            "hostname": host,
            "port": port,
            "use_tls": use_tls,
            "timeout": timeout,
        }

    @staticmethod
    def _build_message(letter: EmailLetter) -> MIMEMultipart:
        message = MIMEMultipart("mixed")
        message["Subject"] = letter.subject
        message["From"] = letter.sender_email
        message["To"] = ", ".join(letter.recipient_emails)
        if letter.cc:
            message["Cc"] = ", ".join(letter.cc)
        if letter.bcc:
            message["Bcc"] = ", ".join(letter.bcc)
        if letter.reply_to is not None:
            message["Reply-To"] = letter.reply_to
        text_part = MIMEMultipart("alternative")
        message.attach(text_part)
        html_part = MIMEText(letter.body_markup, "html", "utf-8")
        text_part.attach(html_part)
        for attachment in letter.attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename={attachment.filename}"
            )
            part.add_header("Content-Type", attachment.content_type)
            message.attach(part)
        return message

    async def send(self, letter: EmailLetter) -> None:
        try:
            logger.info(
                "Start sending email letter to %s, subject %s",
                ", ".join(letter.recipient_emails), letter.subject,
            )
            async with aiosmtplib.SMTP(**self._smtp_config) as server:
                await server.login(self._username, self._password)
                message = self._build_message(letter)
                await server.send_message(message)
                logger.info(
                    "Email successfully sent to %s", ", ".join(letter.recipient_emails)
                )
        except aiosmtplib.SMTPException as e:
            error_message = f"Error occurred while sending email: {e}"
            logger.exception(error_message)
            raise EmailSendingError(error_message) from e
