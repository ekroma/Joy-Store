from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from apps.base.model import Base, HasTranslate

class PromoCodeTypeNames(Enum):
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    PRODUCT = "product"

class PromoCodeTypeSchema(BaseModel):
    type_name:PromoCodeTypeNames = PromoCodeTypeNames.PRODUCT
    content_ids: list[str]

    class Config:
        use_enum_values = True 

class PromoCodeTranslateContent(BaseModel):
    name: str|None = None

class PromoCode(Base, HasTranslate[PromoCodeTranslateContent]):
    __collection_name__:str = 'promocodes'
    _error_num = 6

    type: PromoCodeTypeSchema
    code: str|None = None
    validity: datetime|None = None
    reusable: bool = False
    discount: float
    is_active: bool = True