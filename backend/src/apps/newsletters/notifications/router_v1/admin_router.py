import logging
from bson import ObjectId

from fastapi import APIRouter, status, Query, Body, Security, Depends
from fastapi_versioning import version
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import is_staff, check_permissions
from apps.user_management.user import User
from apps.base import NotFoundException, MessageResponse, PaginationBase, SuccessResponse
from apps.newsletters.notifications import NotificationsService, NotificationStatus, AdminNotificationsUpdate,\
    AdminNotificationsCreate, AdminNotificationsRead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/notifications-admin",
    tags=["yведомления-> Админка"]
)

@router.post("", response_model=AdminNotificationsRead, status_code=status.HTTP_200_OK)
@version(1)
async def create(
        data: AdminNotificationsCreate = Body(...),
        is_authorized: bool = Security(is_staff),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.notifications, "c")
    return await NotificationsService.create_market_notification(data.model_dump(),market=current_user.market)


@router.patch("", response_model=AdminNotificationsRead, status_code=status.HTTP_200_OK)
@version(1)
async def update(
        id:str = Query(...),
        data: AdminNotificationsUpdate = Body(None,),
        is_authorized: bool = Security(is_staff),
        current_user: User = Depends(get_current_user)
        ):
    check_permissions(current_user.permissions.notifications, "u")
    product = await NotificationsService.update(id, data.model_dump(exclude_unset=True), market=current_user.market)
    return product


@router.get("/global", response_model=PaginationBase[AdminNotificationsRead]|AdminNotificationsRead|None, status_code=status.HTTP_200_OK)
@version(1)
async def get_global_notifications(
        is_authorized: bool = Security(is_staff),
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.notifications, "r")
    return await NotificationsService.get_global_notifications(
            id=id,
            page=page,
            page_size=page_size,  
            market=current_user.market)

@router.get("/market", response_model=PaginationBase[AdminNotificationsRead]|AdminNotificationsRead|None, status_code=status.HTTP_200_OK)
@version(1)
async def get_market_notifications(
        is_authorized: bool = Security(is_staff),
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.notifications, "r")
    if id:
        return await NotificationsService.get_by_id(id=id,market=current_user.market)
    return await NotificationsService.get_all(
        page=page,
        page_size=page_size,
        paginate=True,
        filter_criteria={"status":NotificationStatus.MARKET},
        market=current_user.market)

@router.delete("", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def delete(
        id: str = Query(...),
        is_authorized: bool = Security(is_staff),
        current_user: User = Depends(get_current_user),
):
    check_permissions(current_user.permissions.notifications, "d")
    existing_subcategory = await NotificationsService.get_by_id(id, market=current_user.market)
    if not existing_subcategory:
        raise NotFoundException(11)
    await NotificationsService.delete(id=id)
    return SuccessResponse