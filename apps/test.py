import asyncio
import logging

from config.dev import settings
from modules.notifications.domain import EmailLetter
from modules.notifications.infrastructure.email import SMTPEmailSender

email_sender = SMTPEmailSender(
    host="smtp.mail.ru",
    port=465,
    username="andrey.kosov.05@inbox.ru",
    password=settings.mailru.password,
    use_tls=True,
)

test_letter = EmailLetter(
        subject="Тестовое письмо",
        sender_email="andrey.kosov.05@inbox.ru",
        recipient_emails=["andrey.kosov.05@inbox.ru"],
        body_markup="""
            <html>
                <body>
                    <h1>Тестовое письмо</h1>
                    <p>Это <b>тестовое</b> письмо отправлено через SMTP.</p>
                    <p>Время отправки: <i>сейчас</i></p>
                </body>
            </html>
        """,
)


async def main() -> None:
    await email_sender.send(test_letter)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
