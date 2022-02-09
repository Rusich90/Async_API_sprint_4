import orjson
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: str
    name: str
    birth_date: Optional[None] = datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
