import orjson
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Genre(BaseModel):
    __slots__ = ['id', 'name', 'description']
    id: str
    name: str
    description: None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


    '''
    :param search_result: функция получает данные поска Elastic Search в виде словаря
    :return: Возвращается объект FastApi с выставленными данными.
    '''


def create_genres_list(search_result: dict) -> Genre:
    reorganize_es_data = {}
    for slot in Genre.__slots__:
        reorganize_es_data[slot] = search_result['_source'][slot]


    detailed_genre_object = Genre(**reorganize_es_data)
    return detailed_genre_object
