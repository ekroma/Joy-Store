from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from apps.newsletters.notifications import Notification, NotificationStatus, NotificationTranslateContent
from apps.base import HasTranslate

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminNotificationsBase(HasTranslate[NotificationTranslateContent]):
    is_new: bool = True

class AdminNotificationsRead(AdminNotificationsBase):
    status: NotificationStatus
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))

class AdminNotificationsUpdate(AdminNotificationsBase):
    pass

class AdminNotificationsCreate(AdminNotificationsBase):
    pass
