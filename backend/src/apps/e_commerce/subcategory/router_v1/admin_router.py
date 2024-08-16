import logging
from typing import Annotated

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, Depends, Query, Body, status, File, UploadFile
from fastapi_versioning import version
from pydantic.functional_validators import BeforeValidator

from apps.base import MessageResponse, InvalidExtensionException, NotFoundException, FileBase, PaginationBase, SuccessResponse

from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions
from apps.user_management.user import User

from apps.e_commerce.category import CategoryService
from apps.e_commerce.category.exceptions import NotFoundCategoryException
from apps.e_commerce.subcategory.schemas.admin_shemas import AdminSubcategoryCreate, AdminSubcategoryRead, AdminSubcategoryUpdate
from apps.e_commerce.subcategory.exceptions import NotFoundSubcategoryException
from apps.e_commerce.subcategory.subcategory_service import SubcategoryService

PyObjectId = Annotated[str, BeforeValidator(str)]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/subcategory-admin",
    tags=["Подкатегории -> Админская часть"],
)

@router.get("", 
        response_model=PaginationBase[AdminSubcategoryRead]|AdminSubcategoryRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        category_id:str = Query(None),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.subcategory, "r")
    if id:
        return await SubcategoryService.get_by_id(
            id,
            market=current_user.market)
    filter_query = {}
    if category_id:
        filter_query["category_id"] = category_id
    return await SubcategoryService.get_all(
        page,
        page_size, 
        paginate=True,
        filter_criteria=filter_query,
        market=current_user.market)


@router.post("", 
        response_model=AdminSubcategoryRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: AdminSubcategoryCreate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.subcategory, "c")
    category = await CategoryService.get_by_id(
        id=data.category_id,
        market=current_user.market)
    if not category:
        raise NotFoundCategoryException(data.category_id)
    return await SubcategoryService.create(
        data.model_dump(),
        market=current_user.market)


@router.patch("", 
        response_model=AdminSubcategoryRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        subcategory_id: str = Query(...),
        subcategory: AdminSubcategoryUpdate = Body(None),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.subcategory, "u")
    existing_subcategory = await SubcategoryService.get_by_id(subcategory_id,market=current_user.market)
    if not existing_subcategory:
        raise NotFoundSubcategoryException(subcategory_id)
    return await SubcategoryService.update(
        subcategory_id, 
        subcategory.model_dump(exclude_unset=True),
        market=current_user.market)


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        subcategory_id: str = Query(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.subcategory, "d")
    existing_subcategory = await SubcategoryService.get_by_id(subcategory_id,market=current_user.market)
    if not existing_subcategory:
        raise NotFoundSubcategoryException(subcategory_id)
    await SubcategoryService.delete(id=subcategory_id,market=current_user.market)
    return SuccessResponse


@router.patch("/add_file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def add_file(
        id:str,
        image: UploadFile = File(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.subcategory, "u")
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise InvalidExtensionException()
    subcategory = await SubcategoryService.get_by_id(id,market=current_user.market)
    if not subcategory:
        raise NotFoundException(4)
    image_path = await FileBase.save_upload_file(image)
    await SubcategoryService.update(id,{"image":image_path})
    return SuccessResponse

@router.delete("/delete_file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_file(
        id:str,
        image_path: str = Query(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.subcategory, "u")
    subcategory = await SubcategoryService.get_by_id(id,market=current_user.market)
    if not subcategory:
        raise NotFoundException(4)
    if subcategory.image != image_path:
        raise NotFoundException(111)
    await FileBase.delete_file(image_path)
    await SubcategoryService.update(id,{"image":None})
    return SuccessResponse
