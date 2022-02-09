from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.genre import Genre
from services.service import Service


class GenreService(Service):

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_record_from_elastic('genres', genre_id)
        return Genre(**genre['_source'])

    async def get_all(self, size: int, search: Optional[str],
                      search_after: Optional[str]) -> Optional[List[Genre]]:
        genres = await self._get_all('genres', size, search, search_after)
        return [Genre(**genre['_source']) for genre in genres]

    async def get_movies(self, genre_id: str, size: int, search_after: Optional[str]) -> Optional[List[Film]]:
        param = {
            "sort": ["imdb_rating:desc", "id:asc"],
            "size": size,
            "body": {
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
        }

        redis_id = genre_id + 'movies' + str(size)
        if search_after:
            redis_id = redis_id + search_after
            param['body']['search_after'] = search_after.split('_')
        movies = await self._get_movies_from_elastic(redis_id, param)
        return [Film(**movie['_source']) for movie in movies]


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
