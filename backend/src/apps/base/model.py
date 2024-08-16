from pydantic import BaseModel, Field, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Generic, TypeVar
from datetime import datetime
from apps.market.model import Market

T = TypeVar("T")

PyObjectId = Annotated[str, BeforeValidator(str)]

class Base(BaseModel):
    __collection_name__:str|None = None
    _error_num:int|None = None

    id: PyObjectId = Field(None,validation_alias=AliasChoices('_id', 'id'))
    created_at:datetime = Field(default=datetime.now())
    market:Market|None = None

    class Config:
        use_enum_values = True 

class Translate(BaseModel, Generic[T]):
    lang_code:str
    content:T

class HasTranslate(BaseModel,Generic[T]):
    translate_content:list[Translate[T]]|None = None

class Language(Base):
    __collection_name__:str = "language"
    _error_num = 10

    language_code:str
    name:str