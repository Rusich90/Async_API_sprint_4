from functools import lru_cache
from typing import List, Optional

from fastapi import Depends

from db.database import AbstractDataBase
from db.elastic import get_elastic
from models.film import Film
from services.service import Service


class MovieService(Service):

    async def get_by_id(self, movie_id: str) -> Optional[Film]:
        movie = await self.database.get('movies', movie_id)
        if movie:
            movie = Film(**movie['_source'])
        return movie

    async def get_all_by_index(self, path: str, size: int, search: Optional[str],
                               search_after: Optional[str]) -> Optional[List[Film]]:
        movies = await self._get_all(path, 'movies', size, search, search_after)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]

    async def get_movies(self, path: str, query: str, size: int, search_after: Optional[str],
                         detail: Optional[bool] = False) -> Optional[List[Film]]:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fuzziness": "auto",
                    "fields": [
                        "actors_names",
                        "writers_names",
                        "directors_names",
                        "title",
                        "description"
                    ]
                }
            }
        }
        movies = await self._get_movies(path, size, body, search_after, True)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]


@lru_cache()
def get_movie_service(db: AbstractDataBase = Depends(get_elastic)) -> MovieService:
    return MovieService(db)
