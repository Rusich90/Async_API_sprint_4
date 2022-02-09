from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.genre import GenreDetail, GenreList
from models.film import MovieDetail, MovieList
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('', response_model=GenreList)
async def genres_list(size: int = 20, search: str = None, search_after: str = None,
                      genre_service: GenreService = Depends(get_genre_service)) -> GenreList:
    genres = await genre_service.get_all(size, search, search_after)
    genres = [GenreDetail(id=genre.id, name=genre.name) for genre in genres]
    return GenreList(search_after=genre_service.search_after, count=genre_service.count, results=genres)


@router.get('/{genre_id}/movies', response_model=MovieList)
async def genre_movies(genre_id: str, size: int = 20, search_after: str = None,
                       genre_service: GenreService = Depends(get_genre_service)) -> MovieList:
    movies = await genre_service.get_movies(genre_id, size, search_after)
    movies = [MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(search_after=genre_service.search_after, count=genre_service.count, results=movies)


@router.get('/{genre_id}', response_model=GenreDetail)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreDetail(id=genre.id, name=genre.name)
