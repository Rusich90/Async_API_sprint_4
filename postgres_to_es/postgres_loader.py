import psycopg2
from psycopg2.extras import DictCursor

from settings import settings
from utils import backoff


class PostgresLoader:
    """
    Класс для соединения и запросов к postgres
    """
    def __init__(self):
        self.dsn = settings.pg_conf.dsn.dict()
        self.limit = settings.pg_conf.query_limit
        self._connection = None
        self._cursor = None

    def close(self):
        if self._connection:
            if self._cursor:
                self._cursor.close()
            self._connection.close()
        self._connection = None
        self._cursor = None

    def load_movies(self, movies_ids: list, offset: int):
        """
        Метод для запроса фильмов со всеми данными в нужной структуре
        :param movies_ids: лист с айдишниками всех фильмов для обновления
        :param offset: оффсет для запроса пачками
        :return: список фильмов со всеми актерами и жанрами
        """
        query = """
        SELECT
            fw.id, 
            fw.title, 
            fw.description, 
            fw.rating, 
            fw.type, 
            fw.created_at, 
            fw.updated_at, 
            json_agg(distinct jsonb_build_object('name', p.full_name, 'role', pfw.role, 'id', p.id)) as persons,
            json_agg(distinct jsonb_build_object('id', g.id, 'name', g.name)) as genres
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id 
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN %s
        GROUP BY fw.id
        LIMIT {limit} OFFSET {offset};
        """.format(limit=self.limit, offset=offset)
        return self._pg_execute(query, movies_ids)

    def check_updates(self, table: str, date: str) -> list:
        """
        Метод для проверки новых обновлений обновлений
        :param table: название таблицы
        :param date: датаот которой искать обновления
        :return: список айдишников по проверяемой таблице
        """
        query = """
        SELECT *
        FROM content.{table}
        WHERE updated_at > %s
        ORDER BY updated_at
        LIMIT {limit};
        """.format(table=table, limit=self.limit)
        return self._pg_execute(query, date)

    def load_movies_ids(self, table: str, ids: list, offset: int) -> list:
        """
        Метод для запроса айди фильмов из связанных таблиц
        :param table: название таблицы из которой пришли айдишники
        :param ids: айдишники по которым ищем айди фильмов
        :param offset: оффсет для запроса пачками
        :return: список айди фильмов для обновления
        """
        m2m_table = 'person_film_work' if table == 'person' else 'genre_film_work'
        query = """
        SELECT fw.id, fw.updated_at
        FROM content.film_work fw
        LEFT JOIN content.{m2m_table} m2m_fw ON m2m_fw.film_work_id = fw.id
        WHERE m2m_fw.{table}_id IN %s
        ORDER BY fw.updated_at
        LIMIT {limit} OFFSET {offset};
        """.format(m2m_table=m2m_table, table=table, limit=self.limit, offset=offset)
        return self._pg_execute(query, ids)

    @backoff(settings.backoff_start_time, settings.backoff_factor, settings.backoff_border_time)
    def _pg_execute(self, query, param):
        with psycopg2.connect(**self.dsn, cursor_factory=DictCursor) as self._connection:
            with self._connection.cursor() as self._cursor:
                self._cursor.execute(query, (param,))
                return self._cursor.fetchall()
