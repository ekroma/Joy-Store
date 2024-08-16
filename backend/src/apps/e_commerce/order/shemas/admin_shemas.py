from pydantic import BaseModel, Field, AliasChoices
from apps.e_commerce.product import AdminProductRead
from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from datetime import datetime

from apps.e_commerce.order import OrderStatus, Customer
PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminProductItemRead(BaseModel):
    quantity: int
    product:AdminProductRead
    purchase_price: float


class AdminProductItemCreate(BaseModel):
    quantity: int
    product_id:str
    variant_idx:str


class AdminOrderBase(BaseModel):
    address: str|None = None
    customer:Customer|None = None


class AdminOrderRead(AdminOrderBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    total_price: float|None = None
    status: OrderStatus = OrderStatus.PENDING
    products: list[AdminProductItemRead]
    promocodes: list = []

class AdminOrderReadPreCreate(AdminOrderBase):
    total_price: float|None = None
    products: list[AdminProductItemRead]

class AdminOrderList(AdminOrderBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    total_price: float|None = None
    status: OrderStatus = OrderStatus.PENDING
    created_at:datetime

class AdminOrderCreate(AdminOrderBase):
    products: list[AdminProductItemCreate]


class AdminOrderUpdate(AdminOrderBase):
    pass
