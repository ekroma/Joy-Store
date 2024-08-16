from pydantic import Field, BaseModel, AliasChoices, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from apps.user_management.permissions.model import Permissions

from apps.GJ_control_system import Features

from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]


class MarketOwnerCreate(BaseModel):
    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None
    password:str
    phone:str
    permissions: Permissions = Permissions()
    group_id:str|None = None

class MarketOwnerRead(BaseModel):
    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None
    phone:str

class GlobalMarketBase(BaseModel):
    name: str
    description: str
    domain:str
    features: Features = Features()
    address: str|None = None
    contact_details: dict = {}

class GlobalMarketRead(GlobalMarketBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))
    image:str|None = None
    created_at:datetime|None = None
    admin: MarketOwnerRead|None = None

class GlobalMarketUpdate(GlobalMarketBase):
    pass

class GlobalMarketCreate(GlobalMarketBase):
    pass