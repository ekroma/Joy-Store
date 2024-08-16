import logging

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Body, Depends, Security, File, UploadFile
from fastapi_versioning import version

from apps.base import MessageResponse, InvalidExtensionException, NotFoundException, FileBase, PaginationBase, SuccessResponse
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions, is_global
from apps.user_management.user import User

from apps.market.market_service import MarketService
from apps.market.schemas import GlobalMarketRead, GlobalMarketCreate, GlobalMarketUpdate, MarketOwnerCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/market-global-admin",
    tags=["Магазин -> GJ Админская часть"]
)

@router.get("", 
        response_model=PaginationBase[GlobalMarketRead]|GlobalMarketRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.market, "r")
    if id:
        return await MarketService.get_by_id(id)
    return await MarketService.get_all(page=page,page_size=page_size, paginate=True)


@router.post("/", 
        response_model=GlobalMarketRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: GlobalMarketCreate = Body(...),
        admin: MarketOwnerCreate = Body(...),
        is_authorized: bool = Security(is_global),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.market, "c")
    return await MarketService.create(data.model_dump(), admin.model_dump())


@router.patch("/", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        id: str = Query(...),
        data: GlobalMarketUpdate = Body(None),
        is_authorized: bool = Security(is_global),
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user.permissions.market, "u")
    await MarketService.update(id, data.model_dump(exclude_unset=True))
    return SuccessResponse


@router.delete("/", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        id: str = Query(...),
        is_authorized: bool = Security(is_global),
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user.permissions.market, "d")
    await MarketService.delete(id=id)
    return SuccessResponse


@router.patch("/add_file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def add_file(
        id:str,
        image: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_global),):
    check_permissions(current_user.permissions.market, "u")
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise InvalidExtensionException
    market = await MarketService.get_by_id(id)
    if not market:
        raise NotFoundException(1)
    image_path = await FileBase.save_upload_file(image, market=market)
    await MarketService.update(id,{"image":image_path})
    return SuccessResponse


@router.delete("/delete_file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_file(
        id:str,
        image_path: str = Query(...),
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_global)):
    check_permissions(current_user.permissions.market, "u")
    market = await MarketService.get_by_id(id)
    if not market:
        raise NotFoundException(1)
    if market.image != image_path:
        raise NotFoundException(111)
    await FileBase.delete_file(image_path)
    await MarketService.update(id,{"image":None})
    return SuccessResponse