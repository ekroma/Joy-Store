import logging
from fastapi import APIRouter, status, Query, Depends
from fastapi_versioning import version

from apps.base import PaginationBase
from apps.market.model import Market
from apps.market import MarketNotFoundException
from apps.market.dependencies import get_market
from apps.newsletters.notifications import NotificationsService, AdminNotificationsRead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/notifications-client",
    tags=["yведомления-> Клиентская"]
)


@router.get("", response_model=PaginationBase[AdminNotificationsRead]|AdminNotificationsRead|None, status_code=status.HTTP_200_OK)
@version(1)
async def get(
            id: str = Query(None),
            market:Market=Depends(get_market),
            page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    if not market:
        raise MarketNotFoundException()
    if id:
        return await NotificationsService.get_by_id(id=id, market=market)
    return await NotificationsService.get_all(
        page,
        page_size, 
        paginate=True,
        market=market)