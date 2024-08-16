import logging
from fastapi import APIRouter, status, Query, Depends, Body
from fastapi_versioning import version

from apps.base import PaginationBase, NotFoundException
from apps.market.dependencies import get_market
from apps.market.model import Market
from apps.user_management.common.dependencies import get_current_user
from apps.newsletters.messages import ChatService, ChatRead
from apps.user_management.user import User



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/messages-client",
    tags=["сообщения-> Клиентская"]
)


@router.get("", response_model=ChatRead, status_code=status.HTTP_200_OK)
@version(1)
async def get(
            market:Market=Depends(get_market),
            current_user: User = Depends(get_current_user),
            page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    if not market:
        raise NotFoundException()
    return await ChatService.get_chat_by_client_id_or_create(client_id=current_user.id, market=market)


@router.post("", response_model=ChatRead, status_code=status.HTTP_200_OK)
@version(1)
async def create(
        text: str = Body(...),
        current_user: User = Depends(get_current_user),
        market:Market=Depends(get_market)):
    return await ChatService.create_support_message(text=text,client_id=current_user.id,current_user_id=current_user.id,market=market)