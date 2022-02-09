import orjson
from pydantic import BaseModel
from typing import Optional, List


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[None] = str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class GenreDetail(BaseModel):
    id: str
    name: str


class GenreList(BaseModel):
    search_after: Optional[str]
    count: int
    results: List[GenreDetail]
