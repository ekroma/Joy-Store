from fastapi import Depends
from apps.user_management.common.exceptions import NoPermissionException
from apps.user_management.user import User
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.model import AllowedPermissionTypes


def check_permissions(scope:list[AllowedPermissionTypes], need_permissions:tuple[AllowedPermissionTypes]|set[AllowedPermissionTypes]|str)->bool:
    if isinstance(need_permissions, str):
        need_permissions_set = {AllowedPermissionTypes(char) for char in need_permissions}
    else:
        need_permissions_set = set(need_permissions)
    if need_permissions_set <= set(scope):
        return True
    raise  NoPermissionException()

def is_global(current_user:User = Depends(get_current_user)) -> bool:
    if not current_user.is_global:
        raise NoPermissionException()
    return True

def is_staff(current_user:User = Depends(get_current_user)) -> bool:
    if not current_user.is_staff:
        raise NoPermissionException()
    return True

def is_active(current_user:User = Depends(get_current_user)) -> bool:
    if not current_user.is_active:
        raise NoPermissionException()
    return True