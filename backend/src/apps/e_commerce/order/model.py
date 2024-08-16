from apps.base.model import Base
from apps.e_commerce.product import Product, ProductVariant
from pydantic import BaseModel, EmailStr, Field, AliasChoices
from typing import Annotated
from enum import Enum
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class OrderStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductItem(BaseModel):
    quantity: int
    product: Product
    purchase_price: float|None = None


class Customer(BaseModel):
    id: PyObjectId = Field(None,validation_alias=AliasChoices('_id', 'id'))
    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None
    phone:str|None = None


class Order(Base):
    __collection_name__  = "order"
    _error_num = 5

    customer: Customer
    description:str|None = None
    address: str
    products: list[ProductItem]
    products_total_quantity:int = 0
    total_price: float = Field(default=0)
    total_gross_profit: float = Field(default=0)
    status:OrderStatus = OrderStatus.PENDING
    promocodes:list[str] = []