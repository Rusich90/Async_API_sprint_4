import copy
import hashlib
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.client import IndicesClient
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.keyword import Keyword, KeywordCash, PageData


KEYWORD_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
film_list = "test"


class FilmListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.keyword_cash_data = None
        self.current_page_data = None

    async def get_by_keyword(self, keyword: Optional[str] = None, page: Optional[int] = None) -> Optional[Keyword]:

        # Уточняю хэш токенов поискового запроса
        tokens_hash = await self._get_keyword_hash(keyword)
        if not self.current_page_data:
            if not page:
                page = 1
            film_list = await self._cash_elastic_cash_cycle(keyword, page)

        else:
            # автоматический поиск следующей страницы поиска
            # берём из кэша или скролим поиск

            if tokens_hash == self.keyword_cash_data.tokens_hash:
                if not page:
                    page = self.current_page_data.scroll_page + 1
                film_list = await self._film_from_cache(keyword, page)
                if not film_list:
                    film_list = await self._scroll_film_from_elastic()
                    if not film_list:
                        return None
                await self._put_page_to_cache(film_list)

            # в случае нвоого поиска обновляем поиск
            elif tokens_hash != self.keyword_cash_data.tokens_hash:
                self.keyword_cash_data = None
                self.current_page_data = None
                film_list = await self._cash_elastic_cash_cycle(keyword, page)

        return film_list

    # Стандартный круг операций при поиске
    async def _cash_elastic_cash_cycle(self, keyword, page):
        film_list = await self._film_from_cache(keyword, page)
        if not film_list:
            film_list = await self._get_film_from_elastic(keyword, page)
            if not film_list:
                return None
            await self._put_page_to_cache(film_list)
        return film_list

    async def _film_from_cache(self, keyword: str, page: Optional[int]) -> Optional[Film]:
        tokens_hash = await self._get_keyword_hash(keyword)
        data = await self.redis.get(tokens_hash)
        if not data:
            return None
        # сначала находим хэш со списком результатов,
        cashed_keyword = KeywordCash.parse_raw(data)

        # если мы обращаемся к предыдущему поиску без указания страниц,
        # или номер странице больше данных в кэше то продолжаем пагинацию
        # если страница в кэше, то восстанавливаем её.
        if page is None:
            self.current_page_data = PageData(
                scroll_page=cashed_keyword.total_pages,
                results_ids=cashed_keyword.pages[str(cashed_keyword.total_pages)], )
            self.keyword_cash_data = KeywordCash(
                tokens_hash=tokens_hash,
                total_pages=cashed_keyword.total_pages,
                scroll_id=cashed_keyword.scroll_id,
                pages={})
            new_object=await self._scroll_film_from_elastic()
            return new_object

        if page > cashed_keyword.total_pages:
            return None

        # Потом достаём всё из хэша
        film_list = []
        for film_id in cashed_keyword.pages[str(page)]:
            data = await self.redis.get(film_id)
            film_list.append(Film.parse_raw(data))

        self.current_page_data = PageData(
            scroll_page=page, results_ids=cashed_keyword.pages[str(page)],)

        self.keyword_cash_data = cashed_keyword

        new_object = Keyword(results=[film for film in film_list],
                             scroll_page=page,
                             total_pages=cashed_keyword.total_pages)

        return new_object

    async def _get_film_from_elastic(self, keyword: str, page_number: int) -> Optional[Keyword]:
        if keyword == 'all':
            query = {"size": 10, "query": {"match_all": {}}}
        else:
            query = {"size": 10, "query": {
                "bool": {"must": [{"match": {"description": keyword}}]}}}
        # Сортировка не разрешает запуск по имени, только по циформым полям
        # Как можно это исправтиь.
        sort_key = 'imdb_rating:desc'
        # sort_key = "_score"
        responce = await self.elastic.search(index='movies', body=query, scroll='5m', sort=sort_key)

        tokens_hash = await self._get_keyword_hash(keyword)
        film_list = self.film_list_from_response(responce)
        self.current_page_data = PageData(
            scroll_page=1, results_ids=[
                film['_source']['id'] for film in film_list], )

        self.keyword_cash_data = KeywordCash(
            tokens_hash=tokens_hash,
            total_pages=1,
            scroll_id=responce['_scroll_id'],
            pages={
                str(
                    self.current_page_data.scroll_page): self.current_page_data.results_ids})

        return self.create_keyword_object(film_list)

    def film_list_from_response(self, response):
        return response['hits']['hits']

    def create_keyword_object(self, film_list):
        return Keyword(results=[Film(**film['_source']) for film in film_list],
                       scroll_page=self.current_page_data.scroll_page,
                       total_pages=self.keyword_cash_data.total_pages)

    async def _get_keyword_hash(self, keyword: str):
        indices_client = IndicesClient(self.elastic)

        tokens = await indices_client.analyze(
            body={
                "analyzer": "standard",
                "text": keyword,
            }
        )

        token_list = list()
        for token in tokens['tokens']:
            token_list.append(token['token'])
        token_list.sort()
        tokens_hash = hashlib.sha256(
            ''.join(token_list).encode('utf8')).hexdigest()

        return tokens_hash

    async def _scroll_film_from_elastic(self):
        responce = await self.elastic.scroll(
            scroll_id=self.keyword_cash_data.scroll_id,
            scroll='1s',
        )

        self.keyword_cash_data.total_pages += 1
        self.current_page_data.scroll_page += 1
        film_list = self.film_list_from_response(responce)
        self.current_page_data.results_ids = [
            film['_source']['id'] for film in film_list]

        return Keyword(results=[Film(**film['_source']) for film in film_list],
                       scroll_page=self.current_page_data.scroll_page,
                       total_pages=self.keyword_cash_data.total_pages)

    async def _put_page_to_cache(self, film_list: list):
        if int(self.current_page_data.scroll_page) > 1:
            self.keyword_cash_data.pages[str(self.current_page_data.scroll_page)] = copy.deepcopy(
                self.current_page_data.results_ids)

        for film in film_list.results:
            await self.redis.set(film.id, film.json(), expire=KEYWORD_CACHE_EXPIRE_IN_SECONDS)
        await self.redis.set(self.keyword_cash_data.tokens_hash,
                             self.keyword_cash_data.json(),
                             expire=KEYWORD_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),) -> FilmListService:
    return FilmListService(redis, elastic)
