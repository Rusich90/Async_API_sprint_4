from abc import ABC, abstractmethod
from typing import Dict, Optional

from core import config
from db.database import AbstractDataBase


class AbstractService(ABC):

    @abstractmethod
    def __init__(self, database):
        self.database = database
        self.expire = config.EXPIRE_TIME
        self.pagination = None
        self.count = None

    @abstractmethod
    async def set_pagination_and_count(self, doc: Dict, movies: bool = None):
        pass

    @abstractmethod
    async def get_by_id(self, record_id: str):
        pass

    @abstractmethod
    async def get_all_by_index(self, size: int, search: Optional[str], search_after: Optional[str]):
        pass

    @abstractmethod
    async def get_movies(self, record_id: str, size: int, search_after: Optional[str], detail: Optional[bool]):
        pass


class Service(AbstractService):
    def __init__(self, database: AbstractDataBase):
        super().__init__(database)

    async def set_pagination_and_count(self, doc: Dict, movies: bool = None) -> None:
        if len(doc['hits']['hits']) > 0:
            self.pagination = doc['hits']['hits'][-1]['_source']['id']
            if movies:
                self.pagination = f"{doc['hits']['hits'][-1]['_source']['imdb_rating']}_{self.pagination}"
        else:
            self.pagination = None
        self.count = doc['hits']['total']['value']

    async def get_by_id(self, record_id: str):
        raise NotImplementedError()

    async def get_all_by_index(self, size: int, search: Optional[str], search_after: Optional[str]):
        raise NotImplementedError()

    async def get_movies(self, record_id: str, size: int, search_after: Optional[str], detail: Optional[bool]):
        raise NotImplementedError()

    async def _get_all(self, index: str, size: int, search: Optional[str], search_after: Optional[str]):
        param = {
            'index': index,
            'sort': 'id:asc',
            'size': size,
            'body': {}
        }
        if search:
            param['body'] = {"query": {"match": {"name": search}}}
        if search_after:
            param['body']['search_after'] = [search_after]
        records = await self.database.get_all(param, search, search_after)
        await self.set_pagination_and_count(records)
        return records

    async def _get_movies(self, record_id: str,
                          size: int,
                          body: Dict,
                          search_after: Optional[str],
                          detail: bool = False):
        param = {
            "index": "movies",
            "sort": ["imdb_rating:desc", "id:asc"],
            "size": size,
            'body': body,
        }

        cache_id = record_id + 'movies' + str(size)
        if detail:
            cache_id = cache_id + 'detail'
        if search_after:
            cache_id = cache_id + search_after
            param['body']['search_after'] = search_after.split('_')
        movies = await self.database.get_all(param=param, cache_key=cache_id)
        await self.set_pagination_and_count(movies, True)
        return movies

