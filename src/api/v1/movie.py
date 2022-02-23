from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from models.film import MovieBaseDetail, MovieAllDetail, MovieList
from services.service import AbstractService
from services.movie import get_movie_service

router = APIRouter()


@router.get('',
            response_model=MovieList,
            tags=['Фильмы'],
            summary='Список всех фильмов',
            description='Список всех фильмов отсортированный по рейтингу.'
                        ' Можно изменить size запроса и сделать поиск по названию фильма',
            )
async def movies_list(request: Request, size: int = 20, search: str = None, pagination: str = None,
                      service: AbstractService = Depends(get_movie_service)) -> MovieList:
    movies = await service.get_all_by_index(str(request.url), size, search, pagination)
    movies = [MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(pagination=service.pagination, count=service.count, results=movies)


@router.get('/search',
            response_model=MovieList,
            tags=['Полнотекстовый поиск'],
            summary='Поиск кинопроизведений',
            description='Полнотекстовый поиск кинопроизведений по совпадению в названии, описании или людях',
            )
async def movie_search(request: Request, query: str, size: int = 20, pagination: str = None,
                        service: AbstractService = Depends(get_movie_service)) -> MovieList:
    movies = await service.get_movies(str(request.url), query, size, pagination)
    movies = [MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(pagination=service.pagination, count=service.count, results=movies)


@router.get('/{movie_id}',
            response_model=MovieAllDetail,
            tags=['Фильмы'],
            summary='Детали фильма',
            description='Детали определенного фильма с описанием, жанрами и персонами',
            )
async def movie_details(movie_id: str, service: AbstractService = Depends(get_movie_service)) -> MovieAllDetail:
    movie = await service.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='movie not found')
    return MovieAllDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating, description=movie.description,
                          genres=movie.genres, actors=movie.actors, directors=movie.directors, writers=movie.writers)
