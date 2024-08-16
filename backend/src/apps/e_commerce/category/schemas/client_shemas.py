from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.e_commerce.subcategory import SubcategoryRead
from apps.e_commerce.category import CategoryTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class CategoryBase(HasTranslate[CategoryTranslateContent]):
    pass

class CategoryDetail(CategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    subcategories: list[SubcategoryRead]
    image:str|None = None
    
class CategoryRead(CategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None

class CategoryUpdate(CategoryBase):
    pass

class CategoryCreate(CategoryBase):
    pass
