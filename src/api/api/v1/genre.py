from http import HTTPStatus
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service


router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str


class Movie(BaseModel):
    id: str
    title: str
    imdb_rating: float


class MovieResponse(BaseModel):
    scroll_id: str
    count: int
    results: List[Movie]


class GenreResponse(BaseModel):
    scroll_id: str
    count: int
    results: List[Genre]


@router.get('', response_model=GenreResponse)
async def genres_list(size: int = 20, search: str = None, scroll_id: str = None,
                      genre_service: GenreService = Depends(get_genre_service)) -> GenreResponse:
    genres = await genre_service.get_all(size, search, scroll_id)
    genres = [Genre(id=genre.id, name=genre.name) for genre in genres]
    return GenreResponse(scroll_id=genre_service.scroll, count=genre_service.count, results=genres)


@router.get('/{genre_id}/movies', response_model=MovieResponse)
async def genre_movies(genre_id: str, size: int = 20, scroll_id: str = None,
                       genre_service: GenreService = Depends(get_genre_service)) -> MovieResponse:
    movies = await genre_service.get_movies(genre_id, size, scroll_id)
    movies = [Movie(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieResponse(scroll_id=genre_service.scroll, count=genre_service.count, results=movies)


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(id=genre.id, name=genre.name)

