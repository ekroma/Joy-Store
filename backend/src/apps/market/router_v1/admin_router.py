import logging

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Depends, Security, Body, Query
from fastapi_versioning import version

from apps.base import MessageResponse, SuccessResponse
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions, is_staff
from apps.user_management.user import User
from apps.market.market_service import MarketService

from apps.market.schemas import AdminMarketRead, AdminMarketUpdate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/market-admin",
    tags=["Магазин -> Админская часть"]
)

@router.get("", 
        response_model=AdminMarketRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=1, seconds=5))])
@version(1)
async def get(
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_staff),):
    return current_user.market

@router.patch("/", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        id: str = Query(...),
        data: AdminMarketUpdate = Body(None),
        is_authorized: bool = Security(is_staff),
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user.permissions.market, "u")
    await MarketService.update(id, data.model_dump(exclude_unset=True))
    return SuccessResponse