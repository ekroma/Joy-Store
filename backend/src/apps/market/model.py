from apps.GJ_control_system import Features
from pydantic import BaseModel, Field, AliasChoices, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]

class Admin(BaseModel):
    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None
    password:str
    phone:str

class Market(BaseModel):
    __collection_name__ = 'markets'
    _error_num = 1

    id: PyObjectId = Field(None,validation_alias=AliasChoices('_id', 'id'))
    created_at:datetime|None = None
    name:str|None = None
    address: str|None = None
    ip: str|None = None
    domain:str|None = None
    image:str|None = None
    description:str|None = None
    contact_details: dict = {}
    features:Features
    admin:Admin|None = None