import orjson
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Film(BaseModel):
    __slots__ = ['id', 'imdb_rating', 'title', 'description', 'directors_names', 'actors_names', 'writers_names', 'genres_names' ]
    id: str
    imdb_rating: float
    title: str
    description: str
    directors_names: set
    actors_names: set
    writers_names: set
    genres_names: set


    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


def create_film_object(search_result: dict) -> Film:

    '''
    :param search_result: функция получает данные поска Elastic Search в виде словаря
    :return: Возвращается объект FastApi с выставленными данными.
    '''

    reorganize_es_data = {}
    for slot in Film.__slots__:
        reorganize_es_data[slot] = search_result['_source'][slot]

    detailed_film_object = Film(**reorganize_es_data)
    return detailed_film_object

def create_film_list(search_result: dict):
    pass