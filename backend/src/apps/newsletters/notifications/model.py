from pydantic import Field, BaseModel
from apps.base.model import Base, HasTranslate
from enum import Enum

class NotificationStatus(Enum):
    GLOBAL = 'global'
    MARKET = 'market'
    CLIENT = 'client'

class NotificationTranslateContent(BaseModel):
    title: str|None = None
    description: str|None = None
    additional_data: str|None = None

class Notification(Base, HasTranslate[NotificationTranslateContent]):
    __collection_name__ = 'notifications'
    _error_num = 11

    is_new: bool = True
    status: NotificationStatus = NotificationStatus.GLOBAL
    recipient_markets_ids: list[str] = []