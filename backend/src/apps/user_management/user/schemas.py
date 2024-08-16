from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from apps.user_management.user.model import UserSettings, Theme
from apps.market.schemas.global_shemas import GlobalMarketRead
from apps.user_management.permissions.model import Permissions, GlobalPermissions

class UserBase(BaseModel):
    email: EmailStr
    first_name: str|None = None
    display_name: str|None = None

class UserChangePassword(BaseModel):
    password:str
    new_password:str
    confirm_password:str

class UserUpdate(UserBase):
    pass

class UserProfile(UserBase):
    created_at:datetime|None = None
    user_settings: UserSettings

class AdminUserProfile(UserProfile):
    is_active:bool
    is_staff:bool
    group:dict|None = None

class AdminUserProfileDetail(AdminUserProfile):
    permissions: Permissions = Permissions()


class GlobalUserProfile(AdminUserProfile):
    market:GlobalMarketRead|None = None

class GlobalUserProfileDetail(AdminUserProfile):
    permissions: GlobalPermissions = GlobalPermissions()

class UserCreate(UserBase):
    password: str
    password_confirm:str
    code:str

class UserCreateAssistantOrAdmin(UserBase):
    password: str
    password_confirm:str
    permissions: Permissions = Permissions()
    group_id:str|None = None


class UserUpdateAssistantOrAdmin(UserBase):
    password: str
    password_confirm:str
    permissions: Permissions = Permissions()
    group_id:str|None = None


class UserCreateGlobalAssistantOrAdmin(UserBase):
    password: str
    password_confirm:str
    permissions: GlobalPermissions = GlobalPermissions()
    group_id:str|None = None


class UserUpdateGlobalAssistantOrAdmin(UserBase):
    password: str
    password_confirm:str
    permissions: GlobalPermissions = GlobalPermissions()
    group_id:str|None = None


class UserSettingsUpdate(BaseModel):
    theme: Theme|None = None
    system_language: str|None = 'ru'
    products_language: str|None = 'ru'
    
    class Config:
        use_enum_values = True 