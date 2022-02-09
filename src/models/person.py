import orjson
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from .film import MovieDetail


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: str
    name: str
    birth_date: Optional[None] = datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonDetail(BaseModel):
    id: str
    name: str


class PersonMovies(BaseModel):
    id: str
    name: str
    actor: Optional[List[MovieDetail]]
    writer: Optional[List[MovieDetail]]
    director: Optional[List[MovieDetail]]


class PersonList(BaseModel):
    search_after: Optional[str]
    count: int
    results: List[Person]
