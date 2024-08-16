from pydantic import BaseModel, Field
from apps.user_management.user import UserBase
from apps.e_commerce.product import ProductRead
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class ProductItemRead(ProductRead):
    quantity: int


class ProductItemCreate(BaseModel):
    quantity: int
    product_id:str
    variant_idx:str


class OrderBase(BaseModel):
    address: str
    phone: str


class OrderRead(OrderBase):
    id: PyObjectId|None = Field(alias="_id")
    total_price: float|None = None
    products: list[ProductItemRead]

class OrderReadPreCreate(OrderBase):
    total_price: float|None = None
    products: list[ProductItemRead]

class OrderCreate(OrderBase):
    products: list[ProductItemCreate]
    address: str|None = None
    phone: str|None = None


class OrderUpdate(OrderBase):
    pass