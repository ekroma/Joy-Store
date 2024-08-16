from pydantic import BaseModel
from apps.base.model import Base, HasTranslate
from apps.e_commerce.subcategory import Subcategory


class CategoryTranslateContent(BaseModel):
    title: str | None = None
    description: str | None = None

class Category(Base, HasTranslate[CategoryTranslateContent]):
    __collection_name__ = 'category'
    _error_num = 3

    image:str|None = None
    icon:str|None = None
    subcategories:list[Subcategory]|None = None