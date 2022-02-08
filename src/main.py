import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.api.v1 import genre, person
from core import config
from db import elastic
from db import redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)


@app.on_event('shutdown')
async def shutdown():
    await elastic.es.close()
    await redis.redis.close()

app.include_router(genre.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(person.router, prefix='/api/v1/persons', tags=['persons'])
