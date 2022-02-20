from abc import ABC, abstractmethod
from typing import Dict, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from db.cache import AbstractCache


class AbstractDataBase(ABC):

    @abstractmethod
    def __init__(self, cache, db):
        self.cache = cache
        self.db = db

    @abstractmethod
    async def get(self, index_name: str, record_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def get_all(self, param: Dict, search: Optional[str] = None,
                      search_after: Optional[str] = None, cache_key: str = None) -> Dict:
        pass


class ElasticDataBase(AbstractDataBase):

    def __init__(self, cache: AbstractCache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

    async def get(self, index_name: str, record_id: str) -> Optional[Dict]:
        record = await self.cache.get(record_id)
        if not record:
            try:
                record = await self.elastic.get(index_name, record_id)
            except NotFoundError:
                return None
            await self.cache.set(record_id, record)
        return record

    async def get_all(self, param: Dict, search: Optional[str] = None,
                      search_after: Optional[str] = None, cache_key: str = None) -> Dict:
        if not cache_key:
            cache_key = param['index'] + str(param['size'])
        if search:
            cache_key = cache_key + search
        if search_after:
            cache_key = cache_key + search_after
        records = await self.cache.get(cache_key)
        if not records:
            records = await self.elastic.search(**param)
            await self.cache.set(cache_key, records)
        return records
