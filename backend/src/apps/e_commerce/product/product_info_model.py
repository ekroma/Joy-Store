from pydantic import BaseModel, Field
from typing import Any
from apps.base.model import Base, HasTranslate
from apps.base import DataTypes
from enum import Enum


class TemplateTypes(Enum):
    ADDITIONAL_INFO = "additional_info"
    PRODUCT_INFO = "product_info"


class TemplateInfo(Base):
    __collection_name__ = 'template_info'
    _error_num = 14

    name:str
    type: str
    fields:list


class ComponentTranslateContent(BaseModel):
    name: str 
    description: str|None = None


class Component(Base,HasTranslate[ComponentTranslateContent]):
    __collection_name__ = 'components'
    _error_num = 17

    type:DataTypes = DataTypes.STRING.value
    value:Any


class ComponentTemplate(Base):
    __collection_name__ = 'component_templates'
    _error_num = 18

    name:str
    description:str|None = None
    components:list[Component]


class ProductVariant(BaseModel):
    is_storage_countable: bool|None = True
    reserved: int = Field(ge=0,default=0)
    quantity_in_storage: int = Field(ge=0,default=0)
    components: list[Component]
    component_template_name: str|None = None
