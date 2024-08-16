from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.e_commerce.subcategory import SubcategoryTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminSubcategoryBase(HasTranslate[SubcategoryTranslateContent]):
    pass


class AdminSubcategoryRead(AdminSubcategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    category_id: str
    image:str|None = None

class AdminSubcategoryUpdate(AdminSubcategoryBase):
    pass


class AdminSubcategoryCreate(AdminSubcategoryBase):
    category_id: PyObjectId
