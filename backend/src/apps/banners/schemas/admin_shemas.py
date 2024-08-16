from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.banners import BannerTranslateContent

from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]



class AdminBannerBase(HasTranslate[BannerTranslateContent]):
    pass

class AdminBannerDetail(AdminBannerBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    icon:str|None = None


class AdminBannerRead(AdminBannerBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    icon:str|None = None
    created_at:datetime|None = None


class AdminBannerUpdate(AdminBannerBase):
    pass

class AdminBannerCreate(AdminBannerBase):
    pass


