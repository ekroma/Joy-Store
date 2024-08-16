from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.newsletters.notifications import NotificationTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class NotificationsBase(HasTranslate[NotificationTranslateContent]):
    is_new: bool = True


class NotificationsRead(NotificationsBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
