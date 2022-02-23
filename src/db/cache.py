from abc import ABC, abstractmethod
from typing import Dict

import orjson
from aioredis import Redis

from core import config


class AbstractCache(ABC):

    @abstractmethod
    def __init__(self, cache):
        self.expire = config.EXPIRE_TIME
        self.cache = cache

    @abstractmethod
    async def get(self, key: str) -> Dict:
        pass

    @abstractmethod
    async def set(self, key: str, data: Dict) -> None:
        pass


class RedisCache(AbstractCache):

    def __init__(self, cache: Redis):
        self.expire = config.EXPIRE_TIME
        self.cache = cache

    async def get(self, key):
        data = await self.cache.get(key)
        if not data:
            return None
        data = orjson.loads(data)
        return data

    async def set(self, key, data):
        await self.cache.set(key, orjson.dumps(data), expire=self.expire)
