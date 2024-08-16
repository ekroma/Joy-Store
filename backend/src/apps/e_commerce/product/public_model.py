from pydantic import Field
from apps.base.model import Base
from apps.user_management.user import User
from datetime import datetime




class ProductVisits(Base):
    __collection_name__ = 'products_visits'
    _error_num = 16

    product_id:str
    registered_users: list[str]=[]
    anonym_users:int = Field(ge=0)
    date:datetime = datetime.today()


class Comment(Base):
    __collection_name__ = 'comments'
    _error_num = 13

    text:str
    user: User
    product_id:str
    rating: float