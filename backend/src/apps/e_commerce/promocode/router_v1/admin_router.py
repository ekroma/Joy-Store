import logging

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Body, Depends
from fastapi_versioning import version
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions
from apps.user_management.user import User
from apps.e_commerce.promocode import AdminPromoCodeCreate,AdminPromoCodeRead,AdminPromoCodeUpdate, PromoCodeService, PromoCodeTypeNames
from apps.base import NotFoundException, MessageResponse, PaginationBase, SuccessResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/promocode-admin",
    tags=["Промокод-> Админка"]
)

@router.post("", 
        response_model=AdminPromoCodeRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        code_length:int=6,
        data: AdminPromoCodeCreate = Body(...),
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.promocode, "c")
    return await PromoCodeService.create(data.model_dump(),code_length, market=current_user.market)


@router.patch("", 
        response_model=AdminPromoCodeRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        id:str = Query(...),
        data: AdminPromoCodeUpdate = Body(None,),
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.promocode, "u")
    promocode = await PromoCodeService.update(
        id,
        data.model_dump(exclude_none=True),
        market=current_user.market)
    return promocode


@router.get("", 
        response_model=PaginationBase[AdminPromoCodeRead]|AdminPromoCodeRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        code: str|None = Query(None, description="PromoCode code to find"),
        type: PromoCodeTypeNames|None = Query(default=None, description="PromoCode type to filter"),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.promocode, "r")
    if code:
        return await PromoCodeService.get_by_code(code,market=current_user.market)
    if type:
        return await PromoCodeService.get_all(
            page, 
            page_size,
            {"type.type_name": type},
            paginate=True,
            market=current_user.market)
    return await PromoCodeService.get_all(
        page,
        page_size, 
        paginate=True,
        market=current_user.market)


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        promocode_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.promocode, "d")
    existing_subcategory = await PromoCodeService.get_by_id(promocode_id,market=current_user.market)
    if not existing_subcategory:
        raise NotFoundException(6)
    await PromoCodeService.delete(id=promocode_id,market=current_user.market)
    return SuccessResponse


@router.delete("/all", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_many(
        type_name: PromoCodeTypeNames = Query(...),
        content_id: str = Query(...),
        current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.promocode, "d")
    await PromoCodeService.delete_many(
        filter_criteria={"type.type_name": type_name, 
                        "type.content_ids": {"$elemMatch": {"$eq": content_id}}},
        market=current_user.market)
    return SuccessResponse