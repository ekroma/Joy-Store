import logging
from bson import ObjectId

from fastapi import APIRouter, status, Body, Security, Depends, Query
from fastapi_versioning import version
from apps.user_management.common.dependencies import get_current_user
from backend.src.apps.user_management.permissions.permissions import is_assistant_or_admin
from apps.user_management.user import User
from apps.base import PaginationBase
from apps.newsletters.messages import ChatService, AdminChatRead, ChatStatus, AdminChatList

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/notifications-admin",
    tags=["yведомления-> Админка"]
)

@router.post("", response_model=AdminChatRead, status_code=status.HTTP_200_OK)
@version(1)
async def create_message(
        text:str = Body(...),
        client_id:str = Body(...),
        is_authorized: bool = Security(is_assistant_or_admin),
        current_user: User = Depends(get_current_user)):
    return await ChatService.create_support_message(text=text,client_id=client_id,current_user_id=current_user.id,market=current_user.market)

@router.get("", response_model=PaginationBase[AdminChatList]|AdminChatRead, status_code=status.HTTP_200_OK)
@version(1)
async def get(
            chat_id:str = Query(None),
            current_user: User = Depends(get_current_user),
            page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    if chat_id:
        return await ChatService.get_by_id(
            id=chat_id,
            market=current_user.market
        )
    return await ChatService.get_all(
        page=page,
        page_size=page_size,
        paginate=True,
        filter_criteria={"status":ChatStatus.SUPPORT_CHAT},
        market=current_user.market)