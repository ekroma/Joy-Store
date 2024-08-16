from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from datetime import datetime

from apps.base import HasTranslate
from apps.e_commerce.promocode import PromoCodeTypeSchema, PromoCodeTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminPromoCodeBase(HasTranslate[PromoCodeTranslateContent]):
    type:PromoCodeTypeSchema
    validity: datetime|None = None
    reusable: bool = False
    discount:float = Field(ge=0)
    code:str|None = None
    is_active: bool = True

class AdminPromoCodeRead(AdminPromoCodeBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))

class AdminPromoCodeUpdate(AdminPromoCodeBase):
    pass

class AdminPromoCodeCreate(AdminPromoCodeBase):
    pass
