import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import genre, person, movie
from core import config
from core.logger import LOGGING
from db import elastic, redis


tags_metadata = [
    {"name": "Полнотекстовый поиск"},
    {"name": "Фильмы"},
    {"name": "Персоны"},
    {"name": "Жанры"}
]

app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    openapi_tags=tags_metadata,
)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)


@app.on_event('shutdown')
async def shutdown():
    await elastic.es.close()
    await redis.redis.close()

app.include_router(genre.router, prefix='/api/v1/genres')
app.include_router(person.router, prefix='/api/v1/persons')
app.include_router(movie.router, prefix='/api/v1/movies')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
