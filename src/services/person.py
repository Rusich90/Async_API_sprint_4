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
from db.database import ElasticDataBase
from db.cache import RedisCache


class PersonService(Service):

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.database.get('persons', person_id)
        if person:
            person = Person(**person['_source'])
        return person

    async def get_all_by_index(self, size: int, search: Optional[str],
                               search_after: Optional[str]) -> Optional[List[Person]]:
        persons = await self._get_all('persons', size, search, search_after)
        return [Person(**person['_source']) for person in persons['hits']['hits']]

    async def get_movies(self, person_id: str, size: int, search_after: Optional[str],
                         detail: bool = False) -> Optional[List[Film]]:
        body = {
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
        movies = await self._get_movies(person_id, size, body, search_after, detail)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    cache = RedisCache(redis)
    db = ElasticDataBase(cache, elastic)
    return PersonService(db)
