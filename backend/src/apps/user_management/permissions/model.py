from pydantic import BeforeValidator, BaseModel, Field, validator, field_validator, ValidationInfo
from typing import Annotated
from apps.base.model import Base
from enum import Enum

PyObjectId = Annotated[str, BeforeValidator(str)]

class AllowedPermissionTypes(str, Enum):
    read = "r"
    create = "c"
    update = "u"
    delete = "d"

class Permissions(BaseModel):
    language: list[AllowedPermissionTypes] = Field(default=["r"])
    category: list[AllowedPermissionTypes] = Field(default=["r"])
    subcategory: list[AllowedPermissionTypes] = Field(default=["r"])
    product: list[AllowedPermissionTypes] = Field(default=["r"])
    component: list[AllowedPermissionTypes] = Field(default=[])
    order: list[AllowedPermissionTypes] = Field(default=[])
    brand: list[AllowedPermissionTypes] = Field(default=["r"])
    promocode: list[AllowedPermissionTypes] = Field(default=[])
    statistic: list[AllowedPermissionTypes] = Field(default=[])
    group: list[AllowedPermissionTypes] = Field(default=[])
    notifications: list[AllowedPermissionTypes] = Field(default=["r"])
    messages: list[AllowedPermissionTypes] = Field(default=[])
    user: list[AllowedPermissionTypes] = Field(default=[])
    banner: list[AllowedPermissionTypes] = Field(default=["r"])

    @field_validator('*')
    @classmethod
    def validate_permissions(cls, v: list[AllowedPermissionTypes], info:ValidationInfo) -> list[AllowedPermissionTypes]:
        allowed_values = [AllowedPermissionTypes.read, AllowedPermissionTypes.create, AllowedPermissionTypes.update, AllowedPermissionTypes.delete]
        if not all(item in allowed_values for item in v):
            raise ValueError(f"Invalid permission values: {v} for field {info}")
        return v

    def set_all_permissions(self):
        for attr in self.model_fields:
            setattr(self, attr, [
                AllowedPermissionTypes.create,
                AllowedPermissionTypes.read,
                AllowedPermissionTypes.update,
                AllowedPermissionTypes.delete])

class GlobalPermissions(Permissions):
    market: list[AllowedPermissionTypes] = Field(default=[])

    def set_all_permissions(self):
        super().set_all_permissions()

class Group(Base):
    __collection_name__ = 'groups'
    _error_num = 9

    name:str = "default groupe"
    permissions: Permissions
