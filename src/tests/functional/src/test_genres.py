from http import HTTPStatus

import pytest

from tests.functional.testdata.es_data import genres


@pytest.mark.asyncio
async def test_genre_detail(create_index, make_get_request, redis_clear):
    test_data = genres[0]
    response = await make_get_request(f'/genres/{test_data["id"]}/')

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data['id']
    assert response.body['name'] == test_data['name']


@pytest.mark.asyncio
async def test_genre_not_found(make_get_request, redis_clear):
    response = await make_get_request('/genres/1111111111111111/')

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body['detail'] == 'genre not found'


@pytest.mark.asyncio
async def test_genres_list(make_get_request, redis_clear):
    response = await make_get_request('/genres/')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(genres)
    assert len(response.body['results']) == len(genres)


@pytest.mark.asyncio
async def test_genres_search(make_get_request, redis_clear):
    test_data = genres[0]
    response = await make_get_request(f'/genres/?search={test_data["name"]}')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['name'] == test_data['name']


@pytest.mark.asyncio
async def test_genres_list_page(make_get_request, redis_clear):
    size = 3
    response = await make_get_request(f'/genres/?size={size}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(genres)
    assert response.body['pagination'] == genres[:size][-1]['id']
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_genres_list_pagination(make_get_request, redis_clear):
    size = 3
    pagination = genres[:size][-1]['id']
    response = await make_get_request(f'/genres/?size={size}&pagination={pagination}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(genres)
    assert response.body['pagination'] == genres[size:][-1]['id']
    assert len(response.body['results']) == len(genres[size:])


@pytest.mark.asyncio
async def test_genre_movies(make_get_request, redis_clear):
    test_data = genres[0]
    response = await make_get_request(f'/genres/{test_data["id"]}/movies/')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == 2
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_genre_movies_page(make_get_request, redis_clear):
    test_data = genres[0]
    size = 1
    response = await make_get_request(f'/genres/{test_data["id"]}/movies/?size={size}')

    assert response.status == HTTPStatus.OK
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_genre_movies_pagination(make_get_request, redis_clear):
    size = 1
    response = await make_get_request(
        f'/genres/120a21cf-9097-479e-904a-13dd7198c1dd/movies/?size={size}&pagination=8.7_d755d600-296a-4c91-98b9-17107a5e63f5'
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body['results']) == size
