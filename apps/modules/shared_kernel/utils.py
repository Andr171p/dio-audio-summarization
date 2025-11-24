from datetime import datetime
from uuid import uuid4

from config.base import APP_NAME, TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""
    return datetime.now(TIMEZONE)


def generate_correlation_id() -> str:
    """Генерация уникального correlation id (используется для трассировки взаимодействий
    между приложениями)
    """
    return f"{APP_NAME}--{round(current_datetime().timestamp(), 2)}--{uuid4()}"
