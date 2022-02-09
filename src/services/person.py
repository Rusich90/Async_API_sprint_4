from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.person import Person
from services.service import Service


class PersonService(Service):

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_record_from_elastic('persons', person_id)
        movies = await self.get_movies(person_id=person_id, size=500, search_after=None, detail=True)
        return Person(**person['_source']), movies

    async def get_all(self, size: int, search: Optional[str],
                      search_after: Optional[str]) -> Optional[List[Person]]:
        persons = await self._get_all('persons', size, search, search_after)
        return [Person(**person['_source']) for person in persons]

    async def get_movies(self, person_id: str, size: int, search_after: Optional[str],
                         detail: bool = False) -> Optional[List[Film]]:
        param = {
            "sort": ["imdb_rating:desc", "id:asc"],
            "size": size,
            "body": {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "nested": {
                                    "path": "actors", "query": {
                                        "term": {
                                            "actors.id": {
                                                "value": person_id
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "writers", "query": {
                                        "term": {
                                            "writers.id": {
                                                "value": person_id
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "nested": {
                                    "path": "directors", "query": {
                                        "term": {
                                            "directors.id": {
                                                "value": person_id
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        redis_id = person_id + 'movies' + str(size)
        if detail:
            redis_id = redis_id + 'detail'
        if search_after:
            redis_id = redis_id + search_after
            param['body']['search_after'] = search_after.split('_')
        movies = await self._get_movies_from_elastic(redis_id, param)
        return [Film(**movie['_source']) for movie in movies]


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
