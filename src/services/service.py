from typing import List, Optional

import orjson
from aioredis import Redis
from core import config
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError


class Service:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.redis = redis
        self.expire = config.EXPIRE_TIME
        self.search_after = None
        self.count = None

    async def _add_scroll_and_count(self, doc: dict, movies: bool = None) -> None:
        if len(doc['hits']['hits']) > 0:
            self.search_after = doc['hits']['hits'][-1]['_source']['id']
            if movies:
                self.search_after = f"{doc['hits']['hits'][-1]['_source']['imdb_rating']}_{self.search_after}"
        else:
            self.search_after = None
        self.count = doc['hits']['total']['value']

    async def _get_movies_from_elastic(self, redis_id: str, param: dict) -> List:
        doc = await self._get_record_from_cache(redis_id)
        if not doc:
            doc = await self.elastic.search(**param, index='movies')
            await self._put_record_to_cache(redis_id, doc)
        await self._add_scroll_and_count(doc=doc, movies=True)
        movies = doc['hits']['hits']
        return movies

    async def _get_all_records_from_elastic(self, param: dict, search: Optional[str],
                                            search_after: Optional[str]) -> List:
        redis_id = param['index'] + str(param['size'])
        if search:
            redis_id = redis_id + search
        if search_after:
            redis_id = redis_id + search_after
        doc = await self._get_record_from_cache(redis_id)
        if not doc:
            doc = await self.elastic.search(**param)
            await self._put_record_to_cache(redis_id, doc)
        await self._add_scroll_and_count(doc)
        records = doc['hits']['hits']
        return records

    async def _get_record_from_elastic(self, index_name: str, record_id: str) -> Optional[dict]:
        record = await self._get_record_from_cache(record_id)
        if not record:
            try:
                record = await self.elastic.get(index_name, record_id)
            except NotFoundError:
                return None
            await self._put_record_to_cache(record_id, record)
        return record

    async def _get_all(self, index_name: str, size: int, search: Optional[str], search_after: Optional[str]) -> List:
        param = {'index': index_name,
                 'sort': 'id:asc',
                 'size': size,
                 'body': {}}
        if search:
            param['body'] = {"query": {"match": {"name": search}}}
        if search_after:
            param['body']['search_after'] = [search_after]
        records = await self._get_all_records_from_elastic(param, search, search_after)
        return records

    async def _get_record_from_cache(self, redis_id: str) -> Optional[dict]:
        data = await self.redis.get(redis_id)
        if not data:
            return None
        data = orjson.loads(data)
        return data

    async def _put_record_to_cache(self, redis_id: str, data: dict) -> None:
        await self.redis.set(redis_id, orjson.dumps(data), expire=self.expire)
