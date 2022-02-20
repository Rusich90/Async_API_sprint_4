from typing import List, Optional

from models.custom_model import CustomModel


class NameId(CustomModel):
    id: str
    name: str


class Film(CustomModel):
    id: str
    imdb_rating: float
    title: str
    description: Optional[str]
    genres_names: list
    directors_names: list
    actors_names: list
    writers_names: list
    actors: List[NameId]
    directors: List[NameId]
    writers: List[NameId]
    genres: List[NameId]


class MovieDetail(CustomModel):
    id: str
    title: str
    imdb_rating: float


class MovieList(CustomModel):
    pagination: Optional[str]
    count: int
    results: List[MovieDetail]