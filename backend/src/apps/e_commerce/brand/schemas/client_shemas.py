from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.base import HasTranslate
from apps.e_commerce.brand import BrandTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class BrandBase(HasTranslate[BrandTranslateContent]):
    pass


class BrandRead(BrandBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    icon:str|None = None
