from pydantic import Field, BaseModel, AliasChoices, field_validator, ValidationInfo
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Any

from apps.base import HasTranslate, DataTypes
from apps.e_commerce.category import AdminCategoryRead
from apps.e_commerce.subcategory import AdminSubcategoryRead
from apps.e_commerce.brand import AdminBrandRead
from apps.e_commerce.product import ProductTranslateContent, Component, ComponentTranslateContent

PyObjectId = Annotated[str, BeforeValidator(str)]


#-----------AdditionalInfo--------------------

class AdditionalTemplateInfoItemCreate(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    fields:dict

class AdditionalInfoKeyValue(BaseModel):
    key:dict
    value:Any

class AdditionalInfoItemCreate(BaseModel):
    fields:list[AdditionalInfoKeyValue]

class AdditionalInfoItemRead(BaseModel):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    type:str|None = None
    name:str|None = None
    fields:list

#-----------Component--------------------------

class ComponentBase(HasTranslate[ComponentTranslateContent]):
    type:DataTypes = DataTypes.STRING

class ComponentInVariantRead(ComponentBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    value:Any

class ComponentRead(ComponentBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))

class ComponentUpdate(ComponentBase):
    pass

class ComponentCreate(ComponentBase):
    pass

#-------Component Template---------------------

class ComponentTemplateBase(BaseModel):
    name:str
    description:str|None = None

class ComponentTemplateRead(ComponentTemplateBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    components:list[ComponentRead]

class ComponentTemplateCreate(ComponentTemplateBase):
    components_ids:list[str]

class ComponentTemplateUpdate(ComponentTemplateBase):
    components_ids:list[str]

#------------ProductVariants-------------------

class ProductVariantComponentCreate(BaseModel):
    pass

class VariantsBase(BaseModel):
    is_storage_countable: bool|None = True
    quantity_in_storage: int|None = Field(ge=0,default=None)

class ComponentCreateInVariant(BaseModel):
    id:str
    value:Any

class ComponentsTemplateCreateInVariant(BaseModel):
    id:str
    values:dict[int,Any]

class VariantsCreate(VariantsBase): 
    components:list[ComponentCreateInVariant]
    component_template:ComponentsTemplateCreateInVariant|None = None

class VariantsRead(VariantsBase):
    components: list[ComponentInVariantRead]
    component_template_name: str|None = None
    reserved: int = Field(ge=0,default=0)

class VariantsUpdate(VariantsCreate):
    pass

#--------------Product--------------------------

class AdminProductBase(HasTranslate[ProductTranslateContent]):
    price: int = Field(ge=0,default=0)
    product_discount: float = Field(ge=0,default=0)
    cost_price: float = Field(ge=0,default=0)
    available: bool = True
    is_deliverable: bool = True

class AdminProductRead(AdminProductBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    images:list[str]=[]
    category: AdminCategoryRead|None = None
    subcategory: AdminSubcategoryRead|None = None
    variants: dict[str,VariantsRead]
    additional_info: AdditionalInfoItemRead|None = None
    brand: AdminBrandRead|None = None

class AdminProductUpdate(AdminProductBase):
    category_id: str|None = None
    subcategory_id: str|None = None
    brand_id: str|None = None
    additional_info_template: AdditionalTemplateInfoItemCreate|None = None
    additional_info: AdditionalInfoItemCreate|None = None

class AdminProductCreate(AdminProductBase):
    category_id: str
    subcategory_id: str
    brand_id: str|None = None
    variants: list[VariantsCreate]|None
    additional_info_template: AdditionalTemplateInfoItemCreate|None = None
    additional_info: AdditionalInfoItemCreate|None = None