import logging
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Body, Depends, Security, HTTPException, Request
from fastapi_versioning import version

from apps.base import LanguageService, LanguageScheme, MessageResponse, NotFoundException, InvalidDataException, SuccessResponse
from apps.user_management.common.dependencies import get_current_user_or_none, get_current_user
from apps.user_management.user import User
from apps.user_management.permissions.permissions import check_permissions
from apps.market.model import Market
from apps.market.dependencies import get_market
from apps.GJ_control_system import Features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/base",
    tags=["Прочее"]
)

@router.get("/language", 
        response_model=list[LanguageScheme], 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(market:Market|None=Depends(get_market), current_user:User=Depends(get_current_user_or_none)):
    if not market:
        if not current_user:
            raise NotFoundException(1)
        market = current_user.market
    return await LanguageService.get_all(market=market)


@router.post("/language", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: LanguageScheme = Body(...),
        current_user: User = Security(get_current_user)
):
    check_permissions(current_user.permissions.language, "r")
    await LanguageService.create(data.model_dump(),market=current_user.market)
    return SuccessResponse


@router.delete("/language", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        language_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.language, "d")
    existing_subcategory = await LanguageService.get_by_id(language_id,market=current_user.market)
    if not existing_subcategory:
        raise NotFoundException(10)
    await LanguageService.delete(id=language_id)
    return SuccessResponse


@router.get("/features", 
        response_model=Features, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_features(market:Market|None=Depends(get_market),
                    current_user: User = Depends(get_current_user)):
    if not market:
        market = current_user.market
    if not market:
        raise InvalidDataException(1)
    return market.features