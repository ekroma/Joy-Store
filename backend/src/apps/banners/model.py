from pydantic import BaseModel
from apps.base.model import Base, HasTranslate


class BannerTranslateContent(BaseModel):
    title: str | None = None
    description: str | None = None

class Banner(Base, HasTranslate[BannerTranslateContent]):
    __collection_name__ = 'banners'
    _error_num = 19

    name:str
    image:str|None = None
    icon:str|None = None