import math
import secrets
import string
from datetime import timedelta

from modules.shared_kernel.utils import current_datetime


def expires_at(expires_in: timedelta) -> int:
    """Рассчитывает время истечения в Timestamp формате"""

    return math.floor((current_datetime() + expires_in).timestamp())


def generate_guest_name(numbers_count: int = 5) -> str:
    """Генерация гостевого имени

    :param numbers_count: Количество цифр в конце имени.
    """

    numbers = "".join(secrets.choice(string.digits) for _ in range(numbers_count))
    return f"Guest_{numbers}"
