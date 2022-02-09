import orjson
from pydantic import BaseModel
from typing import List

from src.models.film import Film


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PageData(BaseModel):
    scroll_page: int
    results_ids: List[str]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Keyword(BaseModel):
    scroll_page: int
    total_pages: int
    results: List[Film]


class KeywordCash(BaseModel):
    tokens_hash: str
    total_pages: int
    scroll_id: str
    pages: dict

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
