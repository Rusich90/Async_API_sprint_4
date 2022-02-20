from datetime import datetime
from typing import Optional, List

from models.custom_model import CustomModel
from models.film import MovieDetail


class Person(CustomModel):
    id: str
    name: str
    birth_date: Optional[None] = datetime


class PersonDetail(CustomModel):
    id: str
    name: str


class PersonMovies(CustomModel):
    id: str
    name: str
    actor: Optional[List[MovieDetail]]
    writer: Optional[List[MovieDetail]]
    director: Optional[List[MovieDetail]]


class PersonList(CustomModel):
    pagination: Optional[str]
    count: int
    results: List[Person]
