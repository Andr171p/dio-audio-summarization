from datetime import datetime

from config.base import TIMEZONE


def current_datetime() -> datetime:
    """Получение текущего времени в выбранном часовом поясе"""
    return datetime.now(TIMEZONE)
