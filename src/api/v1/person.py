from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from models.person import PersonDetail, PersonList, PersonMovies
from models.film import MovieBaseDetail, MovieList
from services.person import get_person_service
from services.service import AbstractService

router = APIRouter()


@router.get('',
            response_model=PersonList,
            tags=['Персоны'],
            summary='Список всех персон',
            description='Список всех персон. Можно изменить size запроса и сделать поиск по имени персоны',
            )
async def persons_list(request: Request, size: int = 20, search: str = None, pagination: str = None,
                       service: AbstractService = Depends(get_person_service)) -> PersonList:
    persons = await service.get_all_by_index(str(request.url), size, search, pagination)
    persons = [PersonDetail(id=person.id, name=person.name) for person in persons]
    return PersonList(pagination=service.pagination, count=service.count, results=persons)


@router.get('/{person_id}/movies',
            response_model=MovieList,
            tags=['Персоны'],
            summary='Список фильмов по персоне',
            description='Список всех фильмов с определенной персоной отсортированный по рейтингу.'
                        ' Можно изменить size запроса',
            )
async def genre_movies(request: Request, person_id: str, size: int = 20, pagination: str = None,
                       service: AbstractService = Depends(get_person_service)) -> MovieList:
    movies = await service.get_movies(str(request.url), person_id, size, pagination)
    movies = [MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieList(pagination=service.pagination, count=service.count, results=movies)


@router.get('/{person_id}',
            response_model=PersonMovies,
            tags=['Персоны'],
            summary='Детали по персоне',
            description='Детали по персоне со списком фильмов распределенным по ролям'
                        ' (актер, сценарист, режиссер) в произведениях',
            )
async def person_details(request: Request, person_id: str,
                         service: AbstractService = Depends(get_person_service)) -> PersonMovies:
    person = await service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    movies = await service.get_movies(str(request.url), person_id, 500, None)
    actors, writers, directors = [], [], []
    for movie in movies:
        if person.name in movie.actors_names:
            actors.append(MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.writers_names:
            writers.append(MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.directors_names:
            directors.append(MovieBaseDetail(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
    return PersonMovies(id=person.id, name=person.name, actor=actors, writer=writers, director=directors)
