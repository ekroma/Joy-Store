import logging
from fastapi import APIRouter, status, Security, Depends, Query, Body
from fastapi_versioning import version
from apps.user_management.user import UserService,User, AdminUserProfile, AdminUserSettings, UserCreateAssistantOrAdmin,\
    AdminUserProfileDetail
from apps.user_management.permissions import AdminGroupCreate, AdminGroupRead, AdminGroupUpdate
from apps.user_management.permissions.permission_service import GroupService
from apps.base import NotFoundException, PaginationBase, SuccessResponse
from apps.user_management.permissions.permissions import is_staff, check_permissions
from apps.user_management.common.dependencies import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/user-admin",
    tags=["Персонал"]
)


@router.post("/create-assistant-or-admin", response_model=AdminUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def create_assistant_or_admin(
        user: UserCreateAssistantOrAdmin,
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_staff),
        ):
    check_permissions(current_user.permissions.user, "c")
    return await UserService.create_assistant_or_admin(user.model_dump(), market=current_user.market)


@router.post("/update-assistant-or-admin", response_model=AdminUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def update_assistant_or_admin(
        id:str,
        user: UserCreateAssistantOrAdmin,
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_staff)
        ):
    check_permissions(current_user.permissions.user, "u")
    return await UserService.update_assistant_or_admin(id,user.model_dump(), market=current_user.market)


@router.get("/get-user-profile", response_model=AdminUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def get_user_profile(
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/get-users", response_model=PaginationBase[AdminUserProfile]|AdminUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def get_users(
    email:str = Query(None),
    current_user: User = Depends(get_current_user),
    is_authorized: bool = Security(is_staff),
    page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
):
    check_permissions(current_user.permissions.user, "r")
    if email:
        data = await UserService.get_user_by_email(email, market=current_user.market)
    else:
        data = await UserService.get_all(page=page,page_size=page_size,market=current_user.market, paginate=True)
    if not data:
        raise NotFoundException(2)
    return data


@router.patch("/user-settings", response_model=AdminUserProfile, status_code=status.HTTP_200_OK)
@version(1)
async def update_user_settings(
    settings:AdminUserSettings = Body(...),
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user),
):
    return await UserService.update_user(current_user.id, update_data={"user_settings":settings.model_dump()})


#----------Group----------


@router.post("/group", response_model=AdminGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def create_group(
    data:AdminGroupCreate,
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "c")
    return await GroupService.create(data=data.model_dump(), market=current_user.market)


@router.get("/group", response_model=PaginationBase[AdminGroupRead]|AdminGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def get_group(
    id:str|None=None,
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user),
    page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
):
    check_permissions(current_user.permissions.group, "r")
    if id:
        return await GroupService.get_by_id(id=id,market=current_user.market)
    return await GroupService.get_all(
        page=page,
        page_size=page_size,
        paginate=True,
        market=current_user.market)


@router.patch("/group", response_model=AdminGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def update_group(
    id:str,
    data:AdminGroupUpdate,
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "u")
    return await GroupService.update(id=id,update_data=data.model_dump(), market=current_user.market)


@router.delete("/group", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def delete_group(
    id:str,
    data:AdminGroupUpdate,
    is_authorized: bool = Security(is_staff),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "d")
    await GroupService.delete(id=id,market=current_user.market)
    return SuccessResponse