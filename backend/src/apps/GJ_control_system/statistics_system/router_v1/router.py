from apps.user_management.common.dependencies import get_current_user
import logging
from datetime import datetime

from fastapi import APIRouter, status, Security, Body, Query, Depends
from fastapi_versioning import version

from apps.e_commerce.order import OrderService
from apps.user_management.permissions.permissions import is_global
from apps.user_management.user import User
from apps.user_management.permissions.permissions import check_permissions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/global-statistic",
    tags=["gj"]
)

@router.post("/order", status_code=status.HTTP_200_OK)
@version(1)
async def order_stats(from_time:datetime|None = Body(None),
                        to_time:datetime|None = Body(None),
                        is_authorized: bool = Security(is_global),
                        current_user:User = Depends(get_current_user),
                        ):
    check_permissions(current_user.permissions.statistic, "r")
    return await OrderService.get_statistic(from_time=from_time,to_time=to_time)


@router.post("/sales", status_code=status.HTTP_200_OK)
@version(1)
async def sales_stats(from_time:datetime|None = Body(None),
                        to_time:datetime|None = Body(None),
                        is_authorized: bool = Security(is_global),
                        current_user:User = Depends(get_current_user),
                        ):
    check_permissions(current_user.permissions.statistic, "r")
    return await OrderService.get_total_sales_statistic(from_time=from_time,to_time=to_time)


@router.post("/product", status_code=status.HTTP_200_OK)
@version(1)
async def product_stats(from_time:datetime|None = Body(None),
                        to_time:datetime|None = Body(None),
                        is_authorized: bool = Security(is_global),
                        product_id:str = Query(...),
                        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.statistic, "r")
    return await OrderService.get_product_statistics(product_id=product_id,from_time=from_time,to_time=to_time,market=current_user.market)