from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service


router = APIRouter()


class Movie(BaseModel):
    id: str
    title: str
    imdb_rating: float


class Person(BaseModel):
    id: str
    name: str


class PersonDetail(BaseModel):
    id: str
    name: str
    actor: Optional[List[Movie]]
    writer: Optional[List[Movie]]
    director: Optional[List[Movie]]


class MovieResponse(BaseModel):
    search_after: Optional[str]
    count: int
    results: List[Movie]


class PersonResponse(BaseModel):
    search_after: Optional[str]
    count: int
    results: List[Person]


@router.get('', response_model=PersonResponse)
async def persons_list(size: int = 20, search: str = None, search_after: str = None,
                       person_service: PersonService = Depends(get_person_service)) -> PersonResponse:
    persons = await person_service.get_all(size, search, search_after)
    persons = [Person(id=person.id, name=person.name) for person in persons]
    return PersonResponse(search_after=person_service.search_after, count=person_service.count, results=persons)


@router.get('/{person_id}/movies', response_model=MovieResponse)
async def genre_movies(person_id: str, size: int = 20, search_after: str = None,
                       person_service: PersonService = Depends(get_person_service)) -> MovieResponse:
    movies = await person_service.get_movies(person_id, size, search_after)
    movies = [Movie(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating) for movie in movies]
    return MovieResponse(search_after=person_service.search_after, count=person_service.count, results=movies)


@router.get('/{person_id}', response_model=PersonDetail)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonDetail:
    person, movies = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    actors, writers, directors = [], [], []
    for movie in movies:
        if person.name in movie.actors_names:
            actors.append(Movie(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.writers_names:
            writers.append(Movie(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
        if person.name in movie.directors_names:
            directors.append(Movie(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating))
    return PersonDetail(id=person.id, name=person.name, actor=actors, writer=writers, director=directors)

