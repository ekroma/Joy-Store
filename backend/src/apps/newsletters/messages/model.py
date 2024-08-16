from pydantic import BaseModel
from apps.base.model import Base
from enum import Enum
from datetime import datetime
from apps.market.model import Market
from apps.user_management.user import User

class ChatStatus(Enum):
    SUPPORT_CHAT = 'support_chat'

class Messages(BaseModel):
    text: str
    user_id: str
    created_at: datetime

class Chat(Base):
    __collection_name__ = 'chats'

    status: ChatStatus = ChatStatus.SUPPORT_CHAT
    messages: list[Messages]
    client: User
    market: Market|None = None