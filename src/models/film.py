import orjson
from pydantic import BaseModel
from typing import List, Optional

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class NameId(BaseModel):
    id: str
    name: str

class Film(BaseModel):
    id: str
    imdb_rating: float
    title: str
    description: Optional[None] = str
    genres_names: list
    directors_names: list
    actors_names: list
    writers_names: list
    actors: List[NameId]
    directors: List[NameId]
    writers: List[NameId]
    genres: List[NameId]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps