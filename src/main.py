import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.api.v1 import genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis


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
app.include_router(film.router, prefix='/api/v1/film', tags=['film'])
app.include_router(keyword.router, prefix='/api/v1/keyword', tags=['keyword'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
