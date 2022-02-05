from functools import lru_cache
from typing import List, Optional, Union

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from models.person import Person
from services.service import Service


class PersonService(Service):

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._get_record_from_elastic('persons', person_id)
        movies = await self.get_movies(person_id, 100, None)
        return Person(**person['_source']), movies

    async def get_all(self, size: int, search: Union[str, bool],
                      scroll_id: Union[str, bool]) -> Optional[List[Person]]:
        persons = await self._get_all('persons', size, search, scroll_id)
        return [Person(**person['_source']) for person in persons]

    async def get_movies(self, person_id: str, size: int, scroll_id: Optional[str]) -> Optional[List[Film]]:
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
        if scroll_id:
            movies = await self._get_by_scroll(scroll_id)
        else:
            movies = await self._get_movies_from_elastic(body, size)
        return [Film(**movie['_source']) for movie in movies]


@lru_cache()
def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
