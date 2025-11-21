import math
from datetime import timedelta

from modules.shared_kernel.utils import current_datetime


def expires_at(expires_in: timedelta) -> int:
    """Рассчитывает время истечения в Timestamp формате"""
    return math.floor((current_datetime() + expires_in).timestamp())
