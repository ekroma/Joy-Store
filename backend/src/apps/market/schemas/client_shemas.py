from pydantic import Field, BaseModel
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.GJ_control_system import Features

PyObjectId = Annotated[str, BeforeValidator(str)]


class MarketRead(BaseModel):
    name: str
    description: str
    address: str|None
    contact_details: dict = {}
    features: Features = Features()
    image:str|None = None