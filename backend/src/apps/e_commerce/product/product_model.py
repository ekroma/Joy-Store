from pydantic import Field, BaseModel
from apps.base.model import Base, HasTranslate
from apps.e_commerce.category import Category
from apps.e_commerce.subcategory import Subcategory
from apps.e_commerce.brand import Brand
from .product_info_model import ProductVariant, TemplateInfo


class ProductTranslateContent(BaseModel):
    name: str|None = None
    description: str|None = None


class Product(Base, HasTranslate[ProductTranslateContent]):
    __collection_name__ = 'products'
    _error_num = 8

    images:list[str] = []
    brand: Brand|None = None
    price: float = Field(ge=0,default=0)
    product_discount: float = Field(ge=0,default=0)
    cost_price: float = Field(ge=0,default=0)
    available: bool|None = True
    category: Category|None = None
    subcategory: Subcategory|None = None
    variants: dict[str,ProductVariant] = {}
    additional_info: TemplateInfo|dict|None = None
    is_deliverable: bool = True