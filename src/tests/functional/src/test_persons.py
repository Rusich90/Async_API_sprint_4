import pytest


@pytest.mark.asyncio
async def test_person_detail(create_index, make_get_request, redis_clear):
    response = await make_get_request('/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/')

    assert response.status == 200
    assert response.body['id'] == 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    assert response.body['name'] == 'George Lucas'
    assert len(response.body['actor']) == 0
    assert len(response.body['writer']) == 2
    assert len(response.body['director']) == 0


@pytest.mark.asyncio
async def test_person_not_found(make_get_request, redis_clear):
    response = await make_get_request('/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250b/')

    assert response.status == 404
    assert response.body['detail'] == 'person not found'


@pytest.mark.asyncio
async def test_persons_list(make_get_request, redis_clear):
    response = await make_get_request('/persons/')

    assert response.status == 200
    assert response.body['count'] == 8
    assert len(response.body['results']) == 8


@pytest.mark.asyncio
async def test_persons_search(make_get_request, redis_clear):
    response = await make_get_request('/persons/?search=oumakhlouf')

    assert response.status == 200
    assert response.body['count'] == 1
    assert len(response.body['results']) == 1
    assert response.body['results'][0]['id'] == 'd115d4c3-daf9-45ba-8034-1eb07b3be2f3'
    assert response.body['results'][0]['name'] == 'Rachid Oumakhlouf'


@pytest.mark.asyncio
async def test_persons_list_page(make_get_request, redis_clear):
    response = await make_get_request('/persons/?size=5')

    assert response.status == 200
    assert response.body['count'] == 8
    assert response.body['pagination'] == 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    assert len(response.body['results']) == 5


@pytest.mark.asyncio
async def test_persons_list_search_after(make_get_request, redis_clear):
    response = await make_get_request('/persons/?size=5&search_after=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a')

    assert response.status == 200
    assert response.body['count'] == 8
    assert response.body['pagination'] == 'e424a80e-4cf6-4ada-8409-f82056a54564'
    assert len(response.body['results']) == 3


@pytest.mark.asyncio
async def test_person_movies(make_get_request, redis_clear):
    response = await make_get_request('/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/movies/')

    assert response.status == 200
    assert response.body['count'] == 2
    assert len(response.body['results']) == 2


@pytest.mark.asyncio
async def test_person_movies_page(make_get_request, redis_clear):
    response = await make_get_request('/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/movies/?size=1')

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == 1


@pytest.mark.asyncio
async def test_person_movies_search_after(make_get_request, redis_clear):
    response = await make_get_request(
        '/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/movies/?size=1&search_after=8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    )

    assert response.status == 200
    assert response.body['count'] == 2
    assert response.body['pagination'] == '6.2_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == 1
