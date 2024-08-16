import random
from fastapi import HTTPException, status

from apps.base import BaseDAO, NotFoundException, validate_object_id
from apps.user_management.auth.auth import get_password_hash, verify_password
from apps.task_management.newsletter.email import send_email_to_activate_task, send_email_to_restore_task
from apps.user_management.common.exceptions import ChangePasswordException, PasswordsDontMatchException, \
    UserNotFoundException, UserAlreadyExistsException, IncorrectCredentialsException
from .model import User, UserSettings


class UserService(BaseDAO[User]):
    model = User

    @classmethod
    async def pre_register_user(cls, email:str,market=None):
        existing_user = await cls.get_user_by_email(email,additional_fields={"is_active":None}, market=market)
        if existing_user and existing_user.is_active:
            raise UserAlreadyExistsException()
        data:dict={}
        code = ''.join(random.choices('0123456789', k=6))
        send_email_to_activate_task.delay(email=email, subject="Ваша тема", activation_code=code, html=True)
        if existing_user:
            return await cls.update_user(existing_user.id, {"code": code})
        data['email'] = email
        data['code'] = code
        return await cls.create(data, market=market)

    @classmethod
    async def register_user(cls, user_data:dict,market=None):
        existing_user = await cls.get_user_by_email(user_data['email'],additional_fields={"is_active":False},market=market)
        if not existing_user:
            raise UserNotFoundException()
        if  existing_user.code != user_data['code']:
            raise IncorrectCredentialsException
        if user_data['password'] != user_data.pop('password_confirm'):
            raise IncorrectCredentialsException
        password = get_password_hash(user_data['password'])
        user_data['password'] = password
        user_data['is_active'] = True
        return await cls.update(existing_user.id,user_data, market=market)

    @classmethod
    async def create_assistant_or_admin(
            cls, 
            user_data:dict,
            market=None):
        from apps.user_management.permissions.permission_service import GroupService
        existing_user = await cls.get_user_by_email(user_data['email'], market=market)
        if existing_user:
            raise UserAlreadyExistsException()
        if user_data.get('group_id'):
            group = await GroupService.get_by_id(id=user_data['group_id'])
            if not group:
                raise NotFoundException(9)
            user_data['permissions'] = group.permissions.model_dump()
            user_data['group'] = {"name":group.name, "id":group.id}
        password = get_password_hash(user_data['password'])
        user_data['password'] = password
        user_data['is_staff'] = True
        user_data['is_active'] = True
        user_data['user_settings'] = UserSettings().model_dump()
        return await cls.create(user_data, market=market)
    
    @classmethod
    async def update_assistant_or_admin(
            cls, 
            id:str,
            user_data:dict,
            market=None):
        from apps.user_management.permissions.permission_service import GroupService
        existing_user = await cls.get_by_id(id=id, market=market)
        if not existing_user:
            raise NotFoundException(2)
        if user_data.get('permissions'):
            if user_data['permissions'] != existing_user.permissions.model_dump():
                user_data['group'] = None
        password = get_password_hash(user_data['password'])
        user_data['password'] = password
        if user_data.get('group_id'):
            group_id = user_data.pop('group_id')
            if group_id:
                group = await GroupService.get_by_id(id=group_id)
                if not group:
                    raise NotFoundException(9)
                user_data['permissions'] = group.permissions.model_dump()
                user_data['group'] = {"name":group.name, "id":group.id}
            elif group_id == None:
                user_data['group'] = None
        return await cls.update(id=id,update_data=user_data, market=market)

    @classmethod
    async def get_user_by_email(cls, email: str,market=None, additional_fields:dict|None=None)-> User|None:
        collection = await cls.get_collection()
        if additional_fields is None:
            additional_fields={}
        query = {"email": email,'is_active':True}
        for key, value in additional_fields.items():
            query[key] = value
        if market:
            query["market.id"] = market.id
        if query['is_active'] == None:
            del query['is_active']
        user = await collection.find_one(query)
        if not user:
            return None
        return cls.model(**user)

    @classmethod
    async def update_user(cls, user_id: str, update_data: dict) -> User:
        id = validate_object_id(user_id)
        collection = await cls.get_collection()
        await collection.update_one({"_id": id},{"$set": update_data})
        user = await collection.find_one({"_id": id})
        if not user:
            raise NotFoundException(cls.model._error_num)
        return cls.model(**user) #type:ignore

    @classmethod
    async def change_password(
            cls, 
            user:User, 
            old_password: str, 
            new_password: str, 
            new_confirm_password: str,
            market=None) -> str:
        if  not verify_password(old_password, hashed_password=user.password):
            raise ChangePasswordException()

        if new_password != new_confirm_password:
            raise PasswordsDontMatchException()

        new_password_hash = get_password_hash(new_password)
        await cls.update_user(user.id, {"password": new_password_hash})
        return "Password changed"

    @classmethod
    async def pre_restore_password(cls, email:str,market=None):
        existing_user = await cls.get_user_by_email(email, market=market)
        if not existing_user:
            raise NotFoundException(2)
        code = ''.join(random.choices('0123456789', k=6))
        send_email_to_restore_task.delay(email=email, subject="Ваша тема", activation_code=code, html=True)
        return await cls.update_user(existing_user.id,{"code":code})

    @classmethod
    async def restore_password(
            cls, 
            email:str,code:str,
            password:str,confirm_password:str, 
            market=None):
        existing_user = await cls.get_user_by_email(email, market=market)
        if not existing_user:
            raise NotFoundException(2)
        if existing_user.code != code:
            raise HTTPException(status.HTTP_200_OK, "1202995993")
        if password != confirm_password:
            raise HTTPException(status.HTTP_200_OK, "1202994991")
        password = get_password_hash(password)
        return await cls.update_user(existing_user.id,{"password":password})