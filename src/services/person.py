from functools import lru_cache
from typing import List, Optional

from fastapi import Depends

from db.database import AbstractDataBase
from db.elastic import get_elastic
from models.film import Film
from models.person import Person
from services.service import Service


class PersonService(Service):

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.database.get('persons', person_id)
        if person:
            person = Person(**person['_source'])
        return person

    async def get_all_by_index(self, path: str, size: int, search: Optional[str],
                               search_after: Optional[str]) -> Optional[List[Person]]:
        persons = await self._get_all(path, 'persons', size, search, search_after)
        return [Person(**person['_source']) for person in persons['hits']['hits']]

    async def get_movies(self, path: str,  person_id: str, size: int, search_after: Optional[str],
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
        movies = await self._get_movies(path, size, body, search_after)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]


@lru_cache()
def get_person_service(db: AbstractDataBase = Depends(get_elastic)) -> PersonService:
    return PersonService(db)
