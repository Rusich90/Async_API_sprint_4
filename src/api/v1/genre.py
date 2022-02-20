from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.genre import GenreDetail, GenreList
from models.film import MovieDetail, MovieList
from services.service import AbstractService
from services.genre import get_genre_service

router = APIRouter()


@router.get('', response_model=GenreList)
async def genres_list(size: int = 20, search: str = None, search_after: str = None,
                      service: AbstractService = Depends(get_genre_service)) -> GenreList:
    genres = await service.get_all_by_index(size, search, search_after)
    genres = [GenreDetail(id=genre.id, name=genre.name) for genre in genres]
    return GenreList(pagination=service.pagination, count=service.count, results=genres)


@router.get('/{genre_id}/movies', response_model=MovieList)
async def genre_movies(genre_id: str, size: int = 20, search_after: str = None,
                       service: AbstractService = Depends(get_genre_service)) -> MovieList:
    movies = await service.get_movies(genre_id, size, search_after)
    movies = [MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(pagination=service.pagination, count=service.count, results=movies)


@router.get('/{genre_id}', response_model=GenreDetail)
async def genre_details(genre_id: str, service: AbstractService = Depends(get_genre_service)) -> GenreDetail:
    genre = await service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreDetail(id=genre.id, name=genre.name)
