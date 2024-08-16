from apps.base.model import Base, HasTranslate
from typing import Annotated
from pydantic.functional_validators import BeforeValidator
from pydantic import BaseModel

PyObjectId = Annotated[str, BeforeValidator(str)]

class SubcategoryTranslateContent(BaseModel):
    title: str | None
    description: str | None


class Subcategory(Base, HasTranslate[SubcategoryTranslateContent]):
    __collection_name__ = 'subcategory'
    _error_num = 4

    category_id: str| None = None
    image: str|None = None