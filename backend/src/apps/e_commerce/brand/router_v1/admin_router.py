import logging

from fastapi import APIRouter, status, Query, Body, Depends, UploadFile, File, Form
from fastapi_versioning import version

from fastapi_limiter.depends import RateLimiter
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.user import User
from apps.user_management.permissions.permissions import check_permissions
from apps.base import SuccessResponse, NotFoundException, PaginationBase, FileBase, InvalidExtensionException
from apps.e_commerce.brand import BrandService, AdminBrandCreate, AdminBrandUpdate, AdminBrandRead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/brand-admin",
    tags=["Бренд -> Админская часть"]
)

@router.get("", 
        response_model=PaginationBase[AdminBrandRead]|AdminBrandRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.brand, "r")
    if id:
        return await BrandService.get_by_id(id, market=current_user.market)
    return await BrandService.get_all(page=page,page_size=page_size, paginate=True, market=current_user.market)


@router.post("", 
        response_model=AdminBrandRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: AdminBrandCreate = Body(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.brand, "c")
    return await BrandService.create(data.model_dump(), market=current_user.market)


@router.patch("", 
        response_model=AdminBrandRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        brand_id: str = Query(...),
        data: AdminBrandUpdate = Body(None),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.brand,"u")
    return await BrandService.update(brand_id, data.model_dump(exclude_unset=True), market=current_user.market)


@router.patch("/icon", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def icon(
        id:str,
        icon: UploadFile = File(None),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.category, "u")
    brand = await BrandService.get_by_id(id, market=current_user.market)
    if not brand:
        raise NotFoundException(3)
    if brand.icon:
        await FileBase.delete_file(brand.icon)
    query = {}
    if icon:
        if icon.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidExtensionException()
        query['icon'] = await FileBase.save_upload_file(icon, market=current_user.market,destination_path="brand/icons")
    await BrandService.update(id,query)
    return SuccessResponse


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        brand_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.brand, "d")
    existing_subBrand = await BrandService.get_by_id(brand_id, market=current_user.market)
    if not existing_subBrand:
        raise NotFoundException(7)
    await BrandService.delete(brand_id)
    return SuccessResponse