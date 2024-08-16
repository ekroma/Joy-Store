from apps.base.model import Base, HasTranslate
from pydantic import BaseModel

class BrandTranslateContent(BaseModel):
    name: str | None = None
    description: str | None = None


class Brand(Base, HasTranslate[BrandTranslateContent]):
    __collection_name__ = 'brands'
    _error_num = 7

    icon:str|None = None