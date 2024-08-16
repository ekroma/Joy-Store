import logging
from typing import Annotated

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Depends
from fastapi_versioning import version
from pydantic.functional_validators import BeforeValidator
from apps.market.model import Market
from apps.market import MarketNotFoundException
from apps.market.dependencies import get_market
from apps.e_commerce.brand import BrandRead,BrandService
from apps.base import PaginationBase


PyObjectId = Annotated[str, BeforeValidator(str)]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/brand-client",
    tags=["Бренд -> Клиентская часть"]
)


@router.get("", 
        response_model=PaginationBase[BrandRead]|BrandRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
        market:Market=Depends(get_market)):
    if not market:
        raise MarketNotFoundException()
    if id:
        return await BrandService.get_by_id(id, market=market)
    return await BrandService.get_all(page=page,page_size=page_size,market=market, paginate=True)