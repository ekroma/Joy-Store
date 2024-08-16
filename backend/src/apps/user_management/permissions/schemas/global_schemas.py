from pydantic import BaseModel, Field, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.user_management.permissions.model import GlobalPermissions

PyObjectId = Annotated[str, BeforeValidator(str)]


class GlobalGroupBase(BaseModel):
    name:str|None = None
    permissions:GlobalPermissions

class GlobalGroupRead(GlobalGroupBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))

class GlobalGroupCreate(GlobalGroupBase):
    pass

class GlobalGroupUpdate(GlobalGroupBase):
    pass