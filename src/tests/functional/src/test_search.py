from http import HTTPStatus

import pytest

from tests.functional.testdata.es_data import movies


@pytest.mark.asyncio
async def test_search_in_title(make_get_request, redis_clear):
    test_data = movies[1]
    response = await make_get_request('/movies/search/?query=wars')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_search_in_description(make_get_request, redis_clear):
    test_data = movies[0]
    response = await make_get_request('/movies/search/?query=soldiers')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_search_in_actors(make_get_request, redis_clear):
    test_data = movies[2]
    response = await make_get_request('/movies/search/?query=clint')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_search_in_writers(make_get_request, redis_clear):
    test_data = movies[2]
    response = await make_get_request('/movies/search/?query=lucas')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_search_in_directors(make_get_request, redis_clear):
    test_data = movies[1]
    response = await make_get_request('/movies/search/?query=burton')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_search_size(make_get_request, redis_clear):
    size = 2
    response = await make_get_request(f'/movies/search/?query=star&size={size}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_search_pagination(make_get_request, redis_clear):
    size = 2
    response = await make_get_request(
        f'/movies/search/?query=star&size={size}&pagination=0.66033757_d6a7409f-87cd-49d7-8803-951a7352c2ce')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert len(response.body['results']) == len(movies[size:])


@pytest.mark.asyncio
async def test_search_pagination_border(make_get_request, redis_clear):
    response = await make_get_request(
        '/movies/search/?query=star&size=2&pagination=0.14874382_d755d600-296a-4c91-98b9-17107a5e63f5')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert response.body['pagination'] is None
    assert len(response.body['results']) == 0


@pytest.mark.asyncio
async def test_search_none(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=ququq')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == 0
    assert response.body['pagination'] is None
    assert len(response.body['results']) == 0
