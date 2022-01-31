import orjson
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Person(BaseModel):
    __slots__ = ['id', 'name', 'birth_date']
    id: str
    name: str
    birth_date: None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


    '''
    :param search_result: функция получает данные поска Elastic Search в виде словаря
    :return: Возвращается объект FastApi с выставленными данными.
    '''


def create_person_object(search_result: dict) -> Person:
    reorganize_es_data = {}
    for slot in Person.__slots__:
        reorganize_es_data[slot] = search_result['_source'][slot]


    detailed_person_object = Person(**reorganize_es_data)
    return detailed_person_object
