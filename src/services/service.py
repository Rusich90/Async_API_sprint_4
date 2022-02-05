from typing import List, Optional, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError


class Service:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.scroll = None
        self.count = None

    async def _get_by_scroll(self, scroll_id: str) -> List:
        doc = await self.elastic.scroll(scroll_id=scroll_id, scroll='5m')
        await self._add_scroll_and_count(doc)
        records = doc['hits']['hits']
        return records

    async def _add_scroll_and_count(self, doc: dict) -> None:
        self.scroll = doc['_scroll_id']
        self.count = doc['hits']['total']['value']

    async def _get_movies_from_elastic(self, body: dict, size: int) -> List:
        doc = await self.elastic.search(body=body, index='movies', scroll='5m', size=size, sort='imdb_rating:desc')
        await self._add_scroll_and_count(doc)
        movies = doc['hits']['hits']
        return movies

    async def _get_all_records_from_elastic(self, param: dict) -> List:
        doc = await self.elastic.search(**param)
        await self._add_scroll_and_count(doc)
        records = doc['hits']['hits']
        return records

    async def _get_record_from_elastic(self, index_name: str, record_id: str) -> Optional[dict]:
        try:
            record = await self.elastic.get(index_name, record_id)
        except NotFoundError:
            return None
        return record

    async def _get_all(self, index_name: str, size: int, search: Union[str, bool], scroll_id: Union[str, bool]) -> List:
        param = {'index': index_name,
                 'scroll': '5m',
                 'size': size}
        if search:
            param['body'] = {"query": {"match": {"name": search}}}
        if scroll_id:
            records = await self._get_by_scroll(scroll_id=scroll_id)
        else:
            records = await self._get_all_records_from_elastic(param)
        return records
