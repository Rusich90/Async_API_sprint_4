import pytest


@pytest.mark.asyncio
async def test_genre_detail(create_index, make_get_request, redis_clear):
    response = await make_get_request('/genres/6c162475-c7ed-4461-9184-001ef3d9f26e/')

    assert response.status == 200
    assert response.body['id'] == '6c162475-c7ed-4461-9184-001ef3d9f26e'
    assert response.body['name'] == 'Sci-Fi'


@pytest.mark.asyncio
async def test_genre_not_found(make_get_request, redis_clear):
    response = await make_get_request('/genres/a5a8f573-3cee-4ccc-8a2b-91cb9f55250b/')

    assert response.status == 404
    assert response.body['detail'] == 'genre not found'


@pytest.mark.asyncio
async def test_genres_list(make_get_request, redis_clear):
    response = await make_get_request('/genres/')

    assert response.status == 200
    assert response.body['count'] == 4
    assert len(response.body['results']) == 4


@pytest.mark.asyncio
async def test_genres_search(make_get_request, redis_clear):
    response = await make_get_request('/genres/?search=actions')

    assert response.status == 200
    assert response.body['count'] == 1
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff'
    assert response.body['results'][0]['name'] == 'Action'


@pytest.mark.asyncio
async def test_genres_list_page(make_get_request, redis_clear):
    response = await make_get_request('/genres/?size=3')

    assert response.status == 200
    assert response.body['count'] == 4
    assert response.body['pagination'] == '6c162475-c7ed-4461-9184-001ef3d9f26e'
    assert len(response.body['results']) == 3


@pytest.mark.asyncio
async def test_genres_list_search_after(make_get_request, redis_clear):
    response = await make_get_request('/genres/?size=3&search_after=6c162475-c7ed-4461-9184-001ef3d9f26e')

    assert response.status == 200
    assert response.body['count'] == 4
    assert response.body['pagination'] == 'b92ef010-5e4c-4fd0-99d6-41b6456272cd'
    assert len(response.body['results']) == 1


@pytest.mark.asyncio
async def test_genre_movies(make_get_request, redis_clear):
    response = await make_get_request('/genres/120a21cf-9097-479e-904a-13dd7198c1dd/movies/')

    assert response.status == 200
    assert response.body['count'] == 2
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_genre_movies_page(make_get_request, redis_clear):
    response = await make_get_request('/genres/120a21cf-9097-479e-904a-13dd7198c1dd/movies/?size=1')

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '8.7_d755d600-296a-4c91-98b9-17107a5e63f5'
    assert len(response.body['results']) == 1


@pytest.mark.asyncio
async def test_genre_movies_search_after(make_get_request, redis_clear):
    response = await make_get_request(
        '/genres/120a21cf-9097-479e-904a-13dd7198c1dd/movies/?size=1&search_after=8.7_d755d600-296a-4c91-98b9-17107a5e63f5'
    )

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == 1
