from services.keyword import FilmListService, get_film_list_service
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends

router = APIRouter()


@router.get('/{keyword}', response_model=dict)
async def film_details(keyword: str,
                       keyword_service: FilmListService = Depends(get_film_list_service),
                       page: Optional[int] = None):
    film_list = await keyword_service.get_by_keyword(keyword, page)
    if not film_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found')

    return film_list
