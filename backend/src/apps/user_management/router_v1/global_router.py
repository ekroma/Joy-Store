import logging
from fastapi import APIRouter, status, Security, Depends, Query
from fastapi_versioning import version
from apps.base import SuccessResponse
from apps.user_management.user import UserService, User,UserCreateGlobalAssistantOrAdmin, GlobalUserProfile, GlobalUserProfileDetail, UserUpdateGlobalAssistantOrAdmin
from apps.base import PaginationBase
from apps.user_management.permissions.permissions import is_global, check_permissions
from apps.user_management.permissions.permission_service import GroupService
from apps.user_management.permissions.schemas import GlobalGroupCreate,GlobalGroupUpdate,GlobalGroupRead
from apps.user_management.common.dependencies import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/user-global",
    tags=["Персонал Global"]
)


@router.post("/create-global-assistant-or-admin", response_model=GlobalUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def create_assistant_or_admin(
        user: UserCreateGlobalAssistantOrAdmin,
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_global)
        ):
    check_permissions(current_user.permissions.user, "c")
    return await UserService.create_assistant_or_admin(user.model_dump())


@router.post("/update-global-assistant-or-admin", response_model=GlobalUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def update_assistant_or_admin(
        id:str,
        user: UserUpdateGlobalAssistantOrAdmin,
        current_user: User = Depends(get_current_user),
        is_authorized: bool = Security(is_global)
        ):
    check_permissions(current_user.permissions.user, "u")
    return await UserService.update_assistant_or_admin(id,user.model_dump())


@router.get("/get-users", response_model=PaginationBase[GlobalUserProfile]|GlobalUserProfileDetail, status_code=status.HTTP_200_OK)
@version(1)
async def get_users(
    email:str = Query(None),
    domain:str = Query(None),
    current_user: User = Depends(get_current_user),
    is_authorized: bool = Security(is_global),
    page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
):
    check_permissions(current_user.permissions.user, "r")
    filter_criteria = {}
    if email:
        filter_criteria["email"] = email
    if domain:
        filter_criteria["domain"] = domain
    data = await UserService.get_all(page=page,page_size=page_size,filter_criteria=filter_criteria,paginate=True)
    return data


#----------Group----------


@router.post("/group", response_model=GlobalGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def create_group(
    data:GlobalGroupCreate,
    is_authorized: bool = Security(is_global),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "c")
    return await GroupService.create(data=data.model_dump(), market=current_user.market)


@router.get("/group", response_model=PaginationBase[GlobalGroupRead]|GlobalGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def get_group(
    id:str|None=None,
    is_authorized: bool = Security(is_global),
    current_user: User = Depends(get_current_user),
    page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
):
    check_permissions(current_user.permissions.group, "r")
    if id:
        return await GroupService.get_by_id(id=id)
    return await GroupService.get_all(
        page=page,
        page_size=page_size,
        paginate=True)


@router.patch("/group", response_model=GlobalGroupRead, status_code=status.HTTP_200_OK)
@version(1)
async def update_group(
    id:str,
    data:GlobalGroupUpdate,
    is_authorized: bool = Security(is_global),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "u")
    return await GroupService.update(id=id,update_data=data.model_dump())


@router.delete("/group", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
@version(1)
async def delete_group(
    id:str,
    data:GlobalGroupUpdate,
    is_authorized: bool = Security(is_global),
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user.permissions.group, "d")
    await GroupService.delete(id=id,market=current_user.market)
    return SuccessResponse