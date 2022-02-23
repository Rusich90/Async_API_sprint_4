from typing import Optional
from elasticsearch import AsyncElasticsearch

from db.database import AbstractDataBase, ElasticDataBase
from db.redis import get_redis

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AbstractDataBase:
    cache = await get_redis()
    return ElasticDataBase(cache, es)
