from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Any

from datetime import datetime
from apps.base import HasTranslate, DataTypes
from apps.e_commerce.category import CategoryRead
from apps.e_commerce.subcategory import SubcategoryRead
from apps.e_commerce.brand import BrandRead
from apps.e_commerce.product import ProductTranslateContent, ComponentTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdditionalInfoItemRead(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    type:str
    name:str|None = None
    fields:list


class ComponentBase(HasTranslate[ComponentTranslateContent]):
    type:DataTypes = DataTypes.STRING


class ComponentInVariantRead(ComponentBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    value:Any


#------------ProductVariants-------------------

class VariantsBase(BaseModel):
    is_storage_countable: bool|None = True
    quantity_in_storage: int|None = Field(ge=0,default=None)

class VariantsRead(VariantsBase):
    components: list[ComponentInVariantRead]
    component_template_name: str|None = None
    reserved: int = Field(ge=0,default=0)

#--------------Product--------------------------

class ProductBase(HasTranslate[ProductTranslateContent]):
    price: int = Field(ge=0,default=0)
    product_discount: float = Field(ge=0,default=0)
    cost_price: float = Field(ge=0,default=0)
    available: bool = True
    is_deliverable: bool = True

class ProductRead(ProductBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    images:list[str]=[]
    category: CategoryRead|None = None
    subcategory: SubcategoryRead|None = None
    variants: dict[str,VariantsRead]
    additional_info: AdditionalInfoItemRead|None = None
    brand: BrandRead|None = None


class CommentBase(BaseModel):
    text:str
    product_id:str

class CommentUser(BaseModel):
    first_name: str

class CommentRead(CommentBase):
    user: CommentUser
    created_at:datetime
    rating:float = Field(ge=1,le=5)

class CommentCreate(CommentBase):
    rating:int = Field(ge=1,le=5)