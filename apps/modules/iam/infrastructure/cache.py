from modules.shared_kernel.insrastructure.cache import RedisKeyValueCache

from ..application.dto import PKCESession
from ..domain import GuestSession


class PKCESessionCache(RedisKeyValueCache[PKCESession]):
    model = PKCESession


class GuestSessionCache(RedisKeyValueCache[GuestSession]):
    model = GuestSession
