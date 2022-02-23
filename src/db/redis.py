from typing import Optional
from aioredis import Redis

from db.cache import AbstractCache, RedisCache

redis: Optional[Redis] = None


async def get_redis() -> AbstractCache:
    return RedisCache(redis)
