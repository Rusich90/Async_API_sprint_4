import json
import logging.config
import time
from functools import wraps

import requests

from logger_config import LOGGING_CONFIG
from settings import settings

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            t = start_sleep_time
            while True:
                t = t * factor if t < border_sleep_time else border_sleep_time
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    logger.error(f'No connection with service "{func.__name__}"')
                    logger.error('Try to new connect...')
                    logger.error(error)
                    time.sleep(t)
        return inner
    return func_wrapper


def parse_to_elastic(records: list, table: str = None) -> str:
    """
    Функция парсинга из списка фильмов в строку json'ов для эластика
    :param records: список для апдейта
    :param table: название таблицы
    :return: возвращает список json'ов строкой
    """
    table = 'movies' if not table else table
    json_list = []
    for record in records:
        index_info = {'index': {'_index': table + 's', '_id': record['id']}}
        json_list.append(index_info)
        data = {'id': record['id']}

        if table == 'movies':
            directors_names, actors_names, writers_names, actors, writers, directors = [], [], [], [], [], []
            for person in record['persons']:
                if person['role'] == 'director':
                    directors_names.append(person['name'])
                    directors.append({'id': person['id'], 'name': person['name']})
                elif person['role'] == 'actor':
                    actors_names.append(person['name'])
                    actors.append({'id': person['id'], 'name': person['name']})
                elif person['role'] == 'writer':
                    writers_names.append(person['name'])
                    writers.append({'id': person['id'], 'name': person['name']})

            genres_names, genres = [], []
            for genre in record['genres']:
                genres.append({'id': genre['id'], 'name': genre['name']})
                genres_names.append(genre['name'])

            additional_data = {
                'imdb_rating': record['rating'],
                'type': record['type'],
                'title': record['title'],
                'description': record['description'],
                'genres_names': genres_names,
                'directors_names': directors_names,
                'actors_names': actors_names,
                'writers_names': writers_names,
                'actors': actors,
                'directors': directors,
                'writers': writers,
                'genres': genres,
            }

        elif table == 'genre':
            additional_data = {
                'name': record['name'],
                'description': record['description']
            }

        elif table == 'person':
            additional_data = {
                'name': record['full_name'],
                'birth_date': record['birth_date']
            }
        else:
            additional_data = {}

        data.update(additional_data)
        json_list.append(data)

    json_list = '\n'.join(json.dumps(j) for j in json_list)
    json_list += '\n'
    return json_list


@backoff(settings.backoff_start_time, settings.backoff_factor, settings.backoff_border_time)
def request_to_elastic(json_list: str) -> None:
    """
    Функция балк запроса к эластику с обновленными фильмами
    :param json_list: строка со списком json'ов
    :return: None
    """
    url = settings.es_url
    headers = {'content-type': 'application/x-ndjson'}
    response = requests.post(url, data=json_list, headers=headers)
    if response.ok:
        logger.info(f'Successful update in elastic')
    else:
        logger.error(f'Something wrong with elastic: status - "{response.status_code}" response - {response.json()}')
