# import pytest
#
#
# @pytest.mark.asyncio
# async def test_genres_response(create_index, make_get_request, redis_clear):
#     response = await make_get_request('/genres/')
#
#     assert response.status == 200
#     assert len(response.body['results']) == 4
#
#
# @pytest.mark.asyncio
# async def test_persons_response(create_index, make_get_request, redis_clear):
#     response = await make_get_request('/persons/')
#
#     assert response.status == 200
#     assert len(response.body['results']) == 8
#
#
# @pytest.mark.asyncio
# async def test_movies_response(create_index, make_get_request, redis_clear):
#     response = await make_get_request('/keyword/all')
#
#     assert response.status == 200
#     assert len(response.body['results']) == 3
