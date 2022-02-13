import asyncio
import time
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .testdata.es_data import data
from .testdata.es_indexes import genres_index, movies_index, persons_index


SERVICE_URL = 'http://fastapi:8000'
ES_HOST = 'es:9200'
REDIS_HOST = 'redis'


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=ES_HOST)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    redis = await aioredis.create_redis((REDIS_HOST, 6379))
    yield redis
    redis.close()


@pytest.fixture()
async def redis_clear(redis_client):
    yield
    await redis_client.flushall()


@pytest.fixture(scope='session')
async def create_index(es_client):
    await es_client.indices.create(index='genres', body=genres_index)
    await es_client.indices.create(index='persons', body=persons_index)
    await es_client.indices.create(index='movies', body=movies_index)
    await es_client.bulk(body=data)
    time.sleep(1)
    yield
    await es_client.indices.delete(index='_all')


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + '/api/v1' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
