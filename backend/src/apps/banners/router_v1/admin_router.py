import logging

from fastapi import APIRouter, status, Query, Body, Depends, File, UploadFile
from fastapi_versioning import version
from fastapi_limiter.depends import RateLimiter

from apps.base import InvalidExtensionException, NotFoundException, FileBase, PaginationBase, SuccessResponse, InvalidDataException
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions
from apps.user_management.user.model import User
from apps.banners import AdminBannerCreate, AdminBannerUpdate,AdminBannerRead,\
    AdminBannerDetail,BannerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/banner-admin",
    tags=["Баннеры -> Админская часть"]
)

@router.get("", 
        response_model=PaginationBase[AdminBannerDetail]|AdminBannerDetail|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.banner, "r")
    if id:
        return await BannerService.get_by_id(id,market=current_user.market)
    return await BannerService.get_all(page=page,page_size=page_size, market=current_user.market)


@router.post("", 
        response_model=AdminBannerRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: AdminBannerCreate = Body(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.banner, "c")
    return await BannerService.create(data.model_dump(), market=current_user.market)


@router.patch("", 
        response_model=AdminBannerDetail, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        banner_id: str = Query(...),
        data: AdminBannerUpdate = Body(None),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.banner, "u")
    return await BannerService.update(banner_id, data.model_dump(exclude_unset=True), market=current_user.market)


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        banner_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.banner, "d")
    await BannerService.delete(id=banner_id, market=current_user.market)
    return SuccessResponse


@router.patch("/add-file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def add_file(
        id:str,
        icon: UploadFile = File(None),
        image: UploadFile = File(None),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.banner, "u")
    if not icon and not image:
        raise InvalidDataException(111)
    banner = await BannerService.get_by_id(id, market=current_user.market)
    if not banner:
        raise NotFoundException(3)
    if banner.image:
        await FileBase.delete_file(banner.image)
    query = {}
    if image:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidExtensionException()
        query['image'] = await FileBase.save_upload_file(image, market=current_user.market,destination_path="images")
    if icon:
        if icon.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidExtensionException()
        query['icon'] = await FileBase.save_upload_file(icon, market=current_user.market,destination_path="icons")
    await BannerService.update(id,query)
    return SuccessResponse


@router.delete("/delete-file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_file(
        id:str,
        file_path: str = Query(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.banner, "u")
    banner = await BannerService.get_by_id(id,market=current_user.market)
    if not banner:
        raise NotFoundException(3)
    if banner.image == file_path:
        query = {"image":None}
    elif banner.icon == file_path:
        query = {"icon":None}
    else:
        raise NotFoundException(111)
    await FileBase.delete_file(file_path)
    await BannerService.update(id,query)
    return SuccessResponse