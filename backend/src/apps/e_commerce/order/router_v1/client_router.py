import logging
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Body, Depends
from fastapi_versioning import version
from apps.user_management.common.dependencies import get_current_user
from apps.e_commerce.order import OrderRead, OrderService, OrderCreate, OrderReadPreCreate, OrderStatus
from apps.user_management.user import User
from apps.market.model import Market
from apps.market import MarketNotFoundException
from apps.market.dependencies import get_market

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/order-client",
    tags=["Заказы-> Клиентская"]
)

@router.post("/process-order", 
        response_model=OrderReadPreCreate, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def process_order(
        promocodes:list[str] = Body([]),
        data: OrderCreate = Body(...),
        current_user:User = Depends(get_current_user),
        market:Market=Depends(get_market)):
    if not market:
        raise MarketNotFoundException()
    order,_ = await OrderService.process_order(data.model_dump(), promocodes, market=market)
    return order


@router.post("/", 
        response_model=OrderRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        promocodes:list[str] = Body([]),
        data: OrderCreate = Body(...),
        current_user = Depends(get_current_user),
        market:Market=Depends(get_market)):
    if not market:
        raise MarketNotFoundException()
    return await OrderService.create(current_user,data.model_dump(), promocodes, market=market)


@router.patch("/cancel-order", 
        response_model=OrderRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def cancel(
        id:str = Query(...),
        current_user:User = Depends(get_current_user)
        ):
    return await OrderService.cancel_order(id=id, user=current_user, market=current_user.market)


@router.get("/get-user-orders", 
        response_model=list[OrderRead], 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_user_orders(
        current_user = Depends(get_current_user),
        market:Market=Depends(get_market)):
    if not market:
        raise MarketNotFoundException()
    return await OrderService.get_all(filter_criteria={"user.id":current_user._id},market=market)