from pydantic import EmailStr, BeforeValidator, BaseModel, Field, validator
from typing import Annotated
from enum import Enum
from apps.base.model import Base
from apps.user_management.permissions.model import Permissions, GlobalPermissions


PyObjectId = Annotated[str, BeforeValidator(str)]


class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"


class UserSettings(BaseModel):
    theme: Theme = Theme.DARK.value # type: ignore
    system_language: str|None = 'ru'
    products_language: str|None = 'ru'
    data_visibility: bool = True
    
    class Config:
        use_enum_values = True 

class AdminUserSettings(UserSettings):
    default_online_payment_status: bool = True


class GroupSchema(BaseModel):
    name: str|None = "default group"
    id: str


class User(Base):
    __collection_name__ = 'user'
    _error_num = 2

    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None
    password: str|None = None
    refresh_token:str|None = None
    is_active:bool = False
    is_staff:bool = False
    is_global:bool = False
    group: GroupSchema|None = None
    permissions:GlobalPermissions=Field(default=Permissions())
    code:str|None = None
    phone:str|None = None
    user_settings: UserSettings = Field(default=UserSettings())