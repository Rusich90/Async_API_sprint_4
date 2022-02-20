from typing import List, Optional

from models.custom_model import CustomModel


class NameId(CustomModel):
    id: str
    name: str


class Film(CustomModel):
    id: str
    imdb_rating: Optional[float]
    title: str
    description: Optional[str]
    genres_names: List[str]
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    actors: List[NameId]
    directors: List[NameId]
    writers: List[NameId]
    genres: List[NameId]


class MovieBaseDetail(CustomModel):
    id: str
    title: str
    imdb_rating: float


class MovieAllDetail(MovieBaseDetail):
    description: Optional[str]
    genres: List[NameId]
    actors: List[NameId]
    directors: List[NameId]
    writers: List[NameId]


class MovieList(CustomModel):
    pagination: Optional[str]
    count: int
    results: List[MovieBaseDetail]
