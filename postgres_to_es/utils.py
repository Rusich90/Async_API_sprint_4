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


def parse_to_elastic(movies: list) -> str:
    """
    Функция парсинга из списка фильмов в строку json'ов для эластика
    :param movies: список фильмов со всеми актерами и жанрами
    :return: возвращает список json'ов строкой
    """
    json_list = []
    for movie in movies:
        director = None
        actors_names, writers_names, actors, writers = [], [], [], []
        for person in movie['persons']:
            if person['role'] == 'director':
                director = person['name']
            elif person['role'] == 'actor':
                actors_names.append(person['name'])
                actors.append({'id': person['id'], 'name': person['name']})
            elif person['role'] == 'writer':
                writers_names.append(person['name'])
                writers.append({'id': person['id'], 'name': person['name']})

        movie_info = {'index': {'_index': 'movies', '_id': movie['id']}}
        json_list.append(movie_info)
        movie_data = {
            'id': movie['id'],
            'imdb_rating': movie['rating'],
            'type': movie['type'],
            'title': movie['title'],
            'description': movie['description'],
            'director': director,
            'actors_names': actors_names,
            'writers_names': writers_names,
            'genres': movie['genres'],
            'actors': actors,
            'writers': writers,
        }
        json_list.append(movie_data)

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
