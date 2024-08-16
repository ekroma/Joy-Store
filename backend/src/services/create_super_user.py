import os
import sys
import json

cwd = os.getcwd()
sys.path.insert(0, cwd)
apps_path = os.path.abspath(os.path.join(cwd, 'src'))
sys.path.append(apps_path)

from datetime import datetime
from src.apps.user_management.auth.auth import get_password_hash
from src.apps.user_management.permissions.model import GlobalPermissions, AllowedPermissionTypes
from src.apps.user_management.user import UserSettings, User
from config.database import get_db

async def create_admin(data:dict):
    async_db = await get_db()
    collection = async_db['user']
    existing_user = await collection.find_one({"email": email})
    if existing_user:
        raise Exception('User already exists!')
    password = get_password_hash(data['password'])
    permissions = GlobalPermissions()
    permissions.set_all_permissions()
    json_data = User(
        id="None",
        email=data['email'],
        password=password,
        is_global=True,
        is_active=True,
        is_staff=True,
        permissions=permissions.model_dump(), #type:ignore
        market=None,
        user_settings=UserSettings(),
        created_at=datetime.now()
                ).model_dump_json(exclude={"id"})
    await collection.insert_one(json.loads(json_data))


if __name__ == "__main__":
    import asyncio

    email = input('Enter email: ')
    password = input('Enter password: ')

    user_data = {
        "email": email,
        "password": password,
    }
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(create_admin(user_data))
    finally:
        loop.close()
