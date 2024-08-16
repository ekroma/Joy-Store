from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from .settings import settings


async def get_db() -> AsyncIOMotorDatabase: # type: ignore
    async_client = AsyncIOMotorClient(settings.DATABASE_URL_MONGODB)
    async_db = async_client.online_store
    return async_db