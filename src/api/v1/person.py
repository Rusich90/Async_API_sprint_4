from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.person import PersonDetail, PersonList, PersonMovies
from models.film import MovieDetail, MovieList
from services.person import get_person_service
from services.service import AbstractService

router = APIRouter()


@router.get('', response_model=PersonList)
async def persons_list(size: int = 20, search: str = None, search_after: str = None,
                       service: AbstractService = Depends(get_person_service)) -> PersonList:
    persons = await service.get_all_by_index(size, search, search_after)
    persons = [PersonDetail(id=person.id, name=person.name) for person in persons]
    return PersonList(pagination=service.pagination, count=service.count, results=persons)


@router.get('/{person_id}/movies', response_model=MovieList)
async def genre_movies(person_id: str, size: int = 20, search_after: str = None,
                       service: AbstractService = Depends(get_person_service)) -> MovieList:
    movies = await service.get_movies(person_id, size, search_after)
    movies = [MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(pagination=service.pagination, count=service.count, results=movies)


@router.get('/{person_id}', response_model=PersonMovies)
async def person_details(person_id: str, service: AbstractService = Depends(get_person_service)) -> PersonMovies:
    person = await service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    movies = await service.get_movies(person_id, 500, None, True)
    actors, writers, directors = [], [], []
    for movie in movies:
        if person.name in movie.actors_names:
            actors.append(MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.writers_names:
            writers.append(MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.directors_names:
            directors.append(MovieDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
    return PersonMovies(id=person.id, name=person.name, actor=actors, writer=writers, director=directors)
