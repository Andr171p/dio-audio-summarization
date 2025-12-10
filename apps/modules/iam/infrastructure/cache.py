from modules.shared_kernel.insrastructure.cache import RedisKeyValueCache

from ..application.dto import PKCESession


class PKCESessionCache(RedisKeyValueCache[PKCESession]):
    model = PKCESession
