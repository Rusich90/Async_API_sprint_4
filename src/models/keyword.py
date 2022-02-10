from typing import List

from models.film import Film
from models.custom_model import CustomModel


class PageData(CustomModel):
    scroll_page: int
    results_ids: List[str]


class Keyword(CustomModel):
    scroll_page: int
    total_pages: int
    results: List[Film]


class KeywordCash(CustomModel):
    tokens_hash: str
    total_pages: int
    scroll_id: str
    pages: dict
