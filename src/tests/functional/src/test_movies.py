import pytest


@pytest.mark.asyncio
async def test_movie_detail(create_index, make_get_request, redis_clear):
    response = await make_get_request('/movies/d6a7409f-87cd-49d7-8803-951a7352c2ce/')

    assert response.status == 200
    assert response.body['id'] == 'd6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert response.body['title'] == 'Star Wars: Obi-Wan'
    assert response.body['imdb_rating'] == 6.2
    assert response.body['genres'] == [{'id': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', 'name': 'Action'},
                                       {'id': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Sci-Fi'}]
    assert response.body['actors'] == [{'id': '49fe7794-de90-4274-9a50-2be80ca04330', 'name': 'Clint Bajakian'}]
    assert response.body['writers'] == [{'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'name': 'George Lucas'}]
    assert response.body['directors'] == [{'id': '354d7532-386f-48d1-83ab-42c0ff5f146b', 'name': 'Dan Connors'}]


@pytest.mark.asyncio
async def test_movie_not_found(make_get_request, redis_clear):
    response = await make_get_request('/movies/a5a8f573-3cee-4ccc-8a2b-91cb9f55250b/')

    assert response.status == 404
    assert response.body['detail'] == 'movie not found'


@pytest.mark.asyncio
async def test_movies_list(make_get_request, redis_clear):
    response = await make_get_request('/movies/')

    assert response.status == 200
    assert response.body['count'] == 3
    assert len(response.body['results']) == 3


@pytest.mark.asyncio
async def test_movies_search(make_get_request, redis_clear):
    response = await make_get_request('/movies/?search=gold')

    assert response.status == 200
    assert response.body['count'] == 1
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == 'd755d600-296a-4c91-98b9-17107a5e63f5'
    assert response.body['results'][0]['title'] == 'A Gold Star Kid'
    assert response.body['results'][0]['imdb_rating'] == 8.7


@pytest.mark.asyncio
async def test_movies_list_page(make_get_request, redis_clear):
    response = await make_get_request('/movies/?size=2')

    assert response.status == 200
    assert response.body['count'] == 3
    assert response.body['pagination'] == '8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_movies_list_search_after(make_get_request, redis_clear):
    response = await make_get_request('/movies/?size=2&pagination=8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b')

    assert response.status == 200
    assert response.body['count'] == 3
    assert response.body['pagination'] == '6.2_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == 1
