from typing import Optional, List

from models.custom_model import CustomModel


class Genre(CustomModel):
    id: str
    name: str
    description: Optional[None] = str


class GenreDetail(CustomModel):
    id: str
    name: str


class GenreList(CustomModel):
    search_after: Optional[str]
    count: int
    results: List[GenreDetail]
