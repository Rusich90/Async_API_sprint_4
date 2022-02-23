from http import HTTPStatus

import pytest

from tests.functional.testdata.es_data import movies


@pytest.mark.asyncio
async def test_movie_detail(create_index, make_get_request, redis_clear):
    test_data = movies[0]
    response = await make_get_request(f'/movies/{test_data["id"]}/')

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data['id']
    assert response.body['title'] == test_data['title']
    assert response.body['imdb_rating'] == test_data['imdb_rating']
    assert response.body['genres'] == test_data['genres']
    assert response.body['actors'] == test_data['actors']
    assert response.body['writers'] == test_data['writers']
    assert response.body['directors'] == test_data['directors']


@pytest.mark.asyncio
async def test_movie_not_found(make_get_request, redis_clear):
    response = await make_get_request('/movies/1111111/')

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body['detail'] == 'movie not found'


@pytest.mark.asyncio
async def test_movies_list(make_get_request, redis_clear):
    response = await make_get_request('/movies/')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert len(response.body['results']) == len(movies)


@pytest.mark.asyncio
async def test_movies_search(make_get_request, redis_clear):
    test_data = movies[0]
    search_word = test_data['title'].split()[-1]
    response = await make_get_request(f'/movies/?search={search_word}')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['title'] == test_data['title']
    assert response.body['results'][0]['imdb_rating'] == test_data['imdb_rating']


@pytest.mark.asyncio
async def test_movies_list_page(make_get_request, redis_clear):
    size = 2
    response = await make_get_request(f'/movies/?size={size}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert response.body['pagination'] == str(movies[:size][-1]['imdb_rating']) + '_' + movies[:size][-1]['id']
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_movies_list_search_after(make_get_request, redis_clear):
    size = 2
    pagination = str(movies[:size][-1]['imdb_rating']) + '_' + movies[:size][-1]['id']
    response = await make_get_request(f'/movies/?size={size}&pagination={pagination}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(movies)
    assert response.body['pagination'] == str(movies[size:][-1]['imdb_rating']) + '_' + movies[size:][-1]['id']
    assert len(response.body['results']) == len(movies[size:])
