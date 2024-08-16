from pydantic import BaseModel, Field, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.user_management.permissions.model import Permissions

PyObjectId = Annotated[str, BeforeValidator(str)]


class AdminGroupBase(BaseModel):
    name:str|None = None
    permissions:Permissions

class AdminGroupRead(AdminGroupBase):
    id: PyObjectId = Field(validation_alias=AliasChoices('_id', 'id'))

class AdminGroupCreate(AdminGroupBase):
    pass

class AdminGroupUpdate(AdminGroupBase):
    pass