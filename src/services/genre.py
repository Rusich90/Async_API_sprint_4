from functools import lru_cache
from typing import List, Optional, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from models.genre import Genre


class GenreService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
        self.scroll = None
        self.count = None

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        return await self._get_genre_from_elastic(genre_id)

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def get_all(self, size: int, search: Union[str, bool],
                      scroll_id: Union[str, bool]) -> Optional[List[Genre]]:
        param = {'index': 'genres',
                 'scroll': '5m',
                 'size': size}
        if search:
            param['body'] = {"query": {"match": {"name": search}}}
        if scroll_id:
            genres = await self._get_by_scroll(scroll_id=scroll_id)
        else:
            genres = await self._get_all_genre_from_elastic(param)
        return [Genre(**genre['_source']) for genre in genres]

    async def _get_all_genre_from_elastic(self, param: dict) -> List:
        doc = await self.elastic.search(**param)
        await self._add_scroll_and_count(doc)
        genres = doc['hits']['hits']
        return genres

    async def get_movies(self, genre_id: str, size: int, scroll_id: Union[str, bool]) -> Optional[List[Film]]:
        if scroll_id:
            movies = await self._get_by_scroll(scroll_id)
        else:
            movies = await self._get_movies_from_elastic(genre_id, size)
        return [Film(**movie['_source']) for movie in movies]

    async def _get_movies_from_elastic(self, genre_id: str, size: int) -> List:
        body = {
            "query": {
                "nested": {
                    "path": "genres",
                    "query": {
                        "bool": {
                            "must": [{"match": {"genres.id": genre_id}}]
                        }
                    }
                }
            }
        }
        doc = await self.elastic.search(body=body, index='movies', scroll='5m', size=size, sort='imdb_rating:desc')
        await self._add_scroll_and_count(doc)
        movies = doc['hits']['hits']
        return movies

    async def _get_by_scroll(self, scroll_id: str) -> List:
        doc = await self.elastic.scroll(scroll_id=scroll_id, scroll='5m')
        await self._add_scroll_and_count(doc)
        records = doc['hits']['hits']
        return records

    async def _add_scroll_and_count(self, doc: dict) -> None:
        self.scroll = doc['_scroll_id']
        self.count = doc['hits']['total']['value']


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
