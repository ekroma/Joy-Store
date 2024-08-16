from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.e_commerce.subcategory import SubcategoryTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]



class SubcategoryBase(HasTranslate[SubcategoryTranslateContent]):
    pass


class SubcategoryRead(SubcategoryBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    category_id: str | None
