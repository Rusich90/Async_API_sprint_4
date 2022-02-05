from functools import lru_cache
from typing import List, Optional, Union

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from models.genre import Genre
from services.service import Service


class GenreService(Service):

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._get_record_from_elastic('genres', genre_id)
        return Genre(**genre['_source'])

    async def get_all(self, size: int, search: Union[str, bool],
                      scroll_id: Union[str, bool]) -> Optional[List[Genre]]:
        genres = await self._get_all('genres', size, search, scroll_id)
        return [Genre(**genre['_source']) for genre in genres]

    async def get_movies(self, genre_id: str, size: int, scroll_id: Union[str, bool]) -> Optional[List[Film]]:
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
        if scroll_id:
            movies = await self._get_by_scroll(scroll_id)
        else:
            movies = await self._get_movies_from_elastic(body, size)
        return [Film(**movie['_source']) for movie in movies]


@lru_cache()
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
