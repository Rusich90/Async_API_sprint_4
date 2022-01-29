import logging.config
import time

from logger_config import LOGGING_CONFIG
from postgres_loader import PostgresLoader
from settings import settings
from state import State, Storage
from utils import parse_to_elastic, request_to_elastic


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')


def load_data() -> None:
    """
    Основная функция скрипта для обновления записей в эластике
    :return: None
    """
    try:
        while True:
            storage = Storage(settings.pg_conf.state_file_path)
            state = State(storage)

            pg_loader = PostgresLoader()
            movies_ids = set()
            states = {}

            """
            Проходим по каждой таблицы из списка таблиц в конфиге
            """
            for table in settings.pg_conf.tables:
                """
                Берем актуальную дату апдейта из файла состояний, если нету даты, берем дату из конфигурации
                """
                date = state.get_state(table) if state.get_state(table) else settings.pg_conf.default_date

                """
                Проверяем есть ли обновления после даты из состояния
                """
                records_for_update = pg_loader.check_updates(table, date)
                if not records_for_update:
                    logger.info(f'No updates for {table} table')
                    continue
                """
                Запоминаем дату апдейта последней записи в списке в словарь с таблицами и датами
                """
                states[table] = str(records_for_update[-1]['updated_at'])
                ids_list = tuple([record['id'] for record in records_for_update])

                if table == 'film_work':
                    """
                    Если проверяем таблицу с фильмами - то запрос к вспомогательной таблице не делаем
                    """
                    movies_ids.update(ids_list)

                else:
                    """
                    Обновление индексов с жанрами и персонами
                    """
                    json_list = parse_to_elastic(records_for_update, table)
                    request_to_elastic(json_list)

                    """
                    Запрос к вспомогательной таблице и запоминание оффсета для запроса пачками (зависит от query_limit)
                    """
                    offset = 0
                    while True:
                        movies_for_update = pg_loader.load_movies_ids(table, ids_list, offset)
                        if not movies_for_update:
                            break
                        ids = [movie['id'] for movie in movies_for_update]
                        movies_ids.update(ids)
                        offset += pg_loader.limit

            if movies_ids:
                """
                Основной запрос к таблице с фильмами (тоже с оффсетом для запроса пачками)
                """
                offset = 0
                while True:
                    movies = pg_loader.load_movies(tuple(movies_ids), offset)
                    if not movies:
                        break
                    json_list = parse_to_elastic(movies)
                    request_to_elastic(json_list)
                    offset += pg_loader.limit

                """
                Устанавливаем даты для каждой таблицы в состояние после успешного запроса к эластику
                """
                for key, value in states.items():
                    state.set_state(key, value)

            pg_loader.close()
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("ETL process finished!")
    except Exception as error:
        logger.error(f"Something goes wrong! Error - {error}")
    finally:
        pg_loader.close()
        logger.info('Connection with DB closed!')


if __name__ == '__main__':
    logger.info('ETL process started ')
    load_data()
