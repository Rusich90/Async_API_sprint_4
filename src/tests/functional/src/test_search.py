import pytest


@pytest.mark.asyncio
async def test_search_in_title(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=wars')

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '0.83374363_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_search_in_description(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=soldiers')

    assert response.status == 200
    assert response.body['count'] == 1
    assert response.body['pagination'] == '1.266865_d755d600-296a-4c91-98b9-17107a5e63f5'
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == 'd755d600-296a-4c91-98b9-17107a5e63f5'
    assert response.body['results'][0]['title'] == 'A Gold Star Kid'
    assert response.body['results'][0]['imdb_rating'] == 8.7


@pytest.mark.asyncio
async def test_search_in_actors(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=clint')

    assert response.status == 200
    assert response.body['count'] == 1
    assert response.body['pagination'] == '1.135697_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == 'd6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert response.body['results'][0]['title'] == 'Star Wars: Obi-Wan'
    assert response.body['results'][0]['imdb_rating'] == 6.2


@pytest.mark.asyncio
async def test_search_in_writers(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=lucas')

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '0.4700036_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_search_in_directors(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=burton')

    assert response.status == 200
    assert response.body['count'] == 1
    assert response.body['pagination'] == '0.9808291_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == 'daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert response.body['results'][0]['title'] == 'Lego Star Wars: The Video Game'
    assert response.body['results'][0]['imdb_rating'] == 8.2


@pytest.mark.asyncio
async def test_search_size(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=star&size=2')

    assert response.status == 200
    assert response.body['count'] == 3
    assert response.body['pagination'] == '0.66033757_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_search_size(make_get_request, redis_clear):
    response = await make_get_request(
        '/movies/search/?query=star&size=2&pagination=0.66033757_d6a7409f-87cd-49d7-8803-951a7352c2ce')

    assert response.status == 200
    assert response.body['count'] == 3
    assert response.body['pagination'] == '0.14874382_d755d600-296a-4c91-98b9-17107a5e63f5'
    assert len(response.body['results']) == 1


@pytest.mark.asyncio
async def test_search_pagination_border(make_get_request, redis_clear):
    response = await make_get_request(
        '/movies/search/?query=star&size=2&pagination=0.14874382_d755d600-296a-4c91-98b9-17107a5e63f5')

    assert response.status == 200
    assert response.body['count'] == 3
    assert response.body['pagination'] is None
    assert len(response.body['results']) == 0


@pytest.mark.asyncio
async def test_search_none(make_get_request, redis_clear):
    response = await make_get_request('/movies/search/?query=ququq')

    assert response.status == 200
    assert response.body['count'] == 0
    assert response.body['pagination'] is None
    assert len(response.body['results']) == 0
