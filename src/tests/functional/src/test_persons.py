from http import HTTPStatus

import pytest

from tests.functional.testdata.es_data import persons


@pytest.mark.asyncio
async def test_person_detail(create_index, make_get_request, redis_clear):
    test_data = persons[0]
    response = await make_get_request(f'/persons/{test_data["id"]}/')

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data['id']
    assert response.body['name'] == test_data['name']


@pytest.mark.asyncio
async def test_person_not_found(make_get_request, redis_clear):
    response = await make_get_request('/persons/11111111/')

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.body['detail'] == 'person not found'


@pytest.mark.asyncio
async def test_persons_list(make_get_request, redis_clear):
    response = await make_get_request('/persons/')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(persons)
    assert len(response.body['results']) == len(persons)


@pytest.mark.asyncio
async def test_persons_search(make_get_request, redis_clear):
    test_data = persons[0]
    response = await make_get_request(f'/persons/?search={test_data["name"]}')

    assert response.status == HTTPStatus.OK
    assert response.body['results'][0]['id'] == test_data['id']
    assert response.body['results'][0]['name'] == test_data['name']


@pytest.mark.asyncio
async def test_persons_list_page(make_get_request, redis_clear):
    size = 5
    response = await make_get_request(f'/persons/?size={size}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(persons)
    assert response.body['pagination'] == persons[:size][-1]['id']
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_persons_list_pagination(make_get_request, redis_clear):
    size = 5
    pagination = persons[:size][-1]['id']
    response = await make_get_request(f'/persons/?size={size}&pagination={pagination}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == len(persons)
    assert response.body['pagination'] == persons[size:][-1]['id']
    assert len(response.body['results']) == len(persons[size:])


@pytest.mark.asyncio
async def test_person_movies(make_get_request, redis_clear):
    test_data = persons[0]
    response = await make_get_request(f'/persons/{test_data["id"]}/movies/')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == 1
    assert len(response.body['results']) == 1


@pytest.mark.asyncio
async def test_person_movies_page(make_get_request, redis_clear):
    test_data = persons[4]
    size = 1
    response = await make_get_request(f'/persons/{test_data["id"]}/movies/?size={size}')

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == 2
    assert response.body['pagination'] == '8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    assert len(response.body['results']) == size


@pytest.mark.asyncio
async def test_person_movies_pagination(make_get_request, redis_clear):
    size = 1
    response = await make_get_request(
        f'/persons/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a/movies/?size={size}&pagination=8.2_daae47e4-cbd0-4ffd-a150-55201b357d5b'
    )

    assert response.status == HTTPStatus.OK
    assert response.body['count'] == 2
    assert response.body['pagination'] == '6.2_d6a7409f-87cd-49d7-8803-951a7352c2ce'
    assert len(response.body['results']) == size
