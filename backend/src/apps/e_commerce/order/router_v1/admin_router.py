import logging
from bson import ObjectId
from datetime import datetime
from pymongo import ASCENDING

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Body, Depends
from fastapi_versioning import version
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions
from apps.e_commerce.order import AdminOrderRead, OrderService, AdminOrderCreate, AdminOrderUpdate, AdminOrderReadPreCreate, OrderStatus, AdminOrderList
from apps.base import NotFoundException, PaginationBase, SuccessResponse
from apps.user_management.user.model import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/order-admin",
    tags=["Заказы-> Админка"]
)

@router.post("/process-order", 
        response_model=AdminOrderReadPreCreate, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def process_order(
        promocodes:list[str] = Body([]),
        data: AdminOrderCreate = Body(...),
        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.order,"c")
    order = await OrderService.process_order(data.model_dump(), promocodes, market=current_user.market)
    return order


@router.post("", 
        response_model=AdminOrderRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        promocodes:list[str] = Body([]),
        data: AdminOrderCreate = Body(...),
        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.order,"c")
    return await OrderService.create(current_user,data.model_dump(), promocodes, market=current_user.market)


@router.patch("", 
        response_model=AdminOrderRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        id:str = Query(...),
        data: AdminOrderUpdate = Body(None,),
        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.order,"u")
    product = await OrderService.update(id, data.model_dump(exclude_none=True), market=current_user.market)
    return product


@router.get("", 
        # response_model=PaginationBase[AdminOrderList]|AdminOrderRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
            id: str = Query(None),
            email:str|None = None,
            order_status:OrderStatus|None = Query(None, description="allowed values: pending, completed, cancelled or nothing"),
            current_user:User = Depends(get_current_user),
            page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.order,"r")
    if id:
        return await OrderService.get_by_id(id=id,market=current_user.market)
    filter = {}
    if email:
        filter["user.email"] = email
    if order_status:
        filter["status"] = order_status
    return await OrderService.get_all(page,page_size,filter_criteria=filter, 
                                    sort_criteria=[("created_at", ASCENDING)],
                                    paginate=True, 
                                    market=current_user.market)


@router.patch("/cancel-order", 
        response_model=AdminOrderRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def cancel(
        id:str = Query(...),
        current_user:User = Depends(get_current_user)
        ):
    check_permissions(current_user.permissions.order,"u")
    order = await OrderService.cancel_order(id=id, user=current_user, market=current_user.market)
    return order


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        order_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.order,"d")
    existing_order = await OrderService.get_by_id(order_id, market=current_user.market)
    if not existing_order:
        raise NotFoundException(5)
    await OrderService.delete(id=order_id)
    return SuccessResponse


@router.delete("/many", 
        response_model=SuccessResponse,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_many(
        order_ids: list[str] = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.order,"d")
    for order_id in order_ids:
        existing_order = await OrderService.get_by_id(order_id, market=current_user.market)
        if not existing_order:
            raise NotFoundException(5)
        await OrderService.delete_many(filter_criteria={"_id": ObjectId(order_id)}, market=current_user.market)
    return SuccessResponse


@router.post("/order-statistics", 
        response_model=dict, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_statistics(
            from_time:datetime|None = Body(None),
            to_time:datetime|None = Body(None),
            current_user: User = Depends(get_current_user)):
    if not current_user.market:
        raise NotFoundException(1)
    check_permissions(current_user.permissions.statistic,"r")
    return await OrderService.get_statistic(from_time=from_time,to_time=to_time,market=current_user.market)


@router.post("/sales-statistics", 
        response_model=dict, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_sales_statistics(
            from_time:datetime|None = Body(None),
            to_time:datetime|None = Body(None),
            current_user: User = Depends(get_current_user)):
    if not current_user.market:
        raise NotFoundException(1)
    check_permissions(current_user.permissions.statistic,"r")
    return await OrderService.get_total_sales_statistic(from_time=from_time,to_time=to_time,market=current_user.market)



@router.post("/product-statistics", status_code=status.HTTP_200_OK)
@version(1)
async def product_statistics(from_time:datetime|None = Body(None),
                        to_time:datetime|None = Body(None),
                        product_id:str = Query(...),
                        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.statistic,"r")
    return await OrderService.get_product_statistics(product_id=product_id,from_time=from_time,to_time=to_time,market=current_user.market)


@router.post("/popularity_products", status_code=status.HTTP_200_OK)
@version(1)
async def popularity_products(from_time:datetime|None = Body(None),
                        to_time:datetime|None = Body(None),
                        current_user:User = Depends(get_current_user)):
    check_permissions(current_user.permissions.statistic,"r")
    return await OrderService.get_frequently_ordered_products(from_time=from_time,to_time=to_time,market=current_user.market)