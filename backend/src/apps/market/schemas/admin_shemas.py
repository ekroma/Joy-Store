from pydantic import Field, BaseModel
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.GJ_control_system import Features

from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]

class AdminMarketBase(BaseModel):
    name: str
    description: str
    address: str|None
    contact_details: dict = {}

class AdminMarketRead(AdminMarketBase):
    image:str|None = None
    created_at:datetime|None = None
    domain:str 
    features: Features = Features()

class AdminMarketUpdate(AdminMarketBase):
    pass