import logging

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Depends
from fastapi_versioning import version

from apps.market.model import Market
from apps.market import MarketNotFoundException
from apps.market.dependencies import get_market

from apps.market.schemas import MarketRead


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/market-client",
    tags=["Магазин -> Клиентская часть"]
)

@router.get("", 
        response_model=MarketRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=1, seconds=5))])
@version(1)
async def get(
        market:Market=Depends(get_market)):
    if not market:
        raise MarketNotFoundException()
    return market