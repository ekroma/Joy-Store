from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.e_commerce.subcategory.schemas.admin_shemas import AdminSubcategoryRead
from apps.e_commerce.category import CategoryTranslateContent

from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]



class AdminCategoryBase(HasTranslate[CategoryTranslateContent]):
    pass

class AdminCategoryDetail(AdminCategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    subcategories: list[AdminSubcategoryRead]
    image:str|None = None
    icon:str|None = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class AdminCategoryRead(AdminCategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    icon:str|None = None
    created_at:datetime|None = None


class AdminCategoryUpdate(AdminCategoryBase):
    pass

class AdminCategoryCreate(AdminCategoryBase):
    pass


