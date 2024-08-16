from pydantic import BaseModel
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.newsletters.messages import ChatStatus, Messages
from apps.user_management.user import AdminUserProfile

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminChatBase(BaseModel):
    status: ChatStatus = ChatStatus.SUPPORT_CHAT
    client: AdminUserProfile

class AdminChatRead(AdminChatBase):
    messages: list[Messages]

class AdminChatList(AdminChatBase):
    pass
