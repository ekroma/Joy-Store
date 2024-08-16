from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.banners import BannerTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class BannerBase(HasTranslate[BannerTranslateContent]):
    pass

class BannerDetail(BannerBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    icon:str|None = None
    
class BannerRead(BannerBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    icon:str|None = None