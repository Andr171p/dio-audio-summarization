from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import aiosmtplib

from modules.shared_kernel.email import EmailLetter


class SMTPEmailClient:
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
            "hostname": host, "port": port, "use_tls": use_tls, "timeout": timeout,
        }

    def _build_message(self, letter: EmailLetter):
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
        html_part = MIMEText(letter.html_body, "html", "utf-8")
        text_part.attach(html_part)
        for attachment in letter.attachments:
            part = MIMEBase(
                attachment.content_type.split("/")[0],
                attachment.content_type.split("/")[1] if "/" in attachment.content_type else "octet-stream"
            )
            part.set_payload(attachment.content)
            encoders.encode_base64(part)

    async def send_letter(self, letter: EmailLetter) -> None:
        ...
