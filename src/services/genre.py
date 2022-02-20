from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from db.database import ElasticDataBase
from db.cache import RedisCache
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.genre import Genre
from services.service import Service


class GenreService(Service):

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self.database.get('genres', genre_id)
        if genre:
            genre = Genre(**genre['_source'])
        return genre

    async def get_all_by_index(self, size: int, search: Optional[str],
                               search_after: Optional[str]) -> Optional[List[Genre]]:
        genres = await self._get_all('genres', size, search, search_after)
        return [Genre(**genre['_source']) for genre in genres['hits']['hits']]

    async def get_movies(self, genre_id: str, size: int, search_after: Optional[str],
                         detail: Optional[bool] = False) -> Optional[List[Film]]:
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
        movies = await self._get_movies(genre_id, size, body, search_after)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    cache = RedisCache(redis)
    db = ElasticDataBase(cache, elastic)
    return GenreService(db)
