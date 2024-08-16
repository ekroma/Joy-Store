from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from apps.user_management.user import UserService
from fastapi_limiter import FastAPILimiter
import asyncio
from .settings import settings

redis_client = None

async def create_indexes():
    collection = await UserService.get_collection()
    index_info = None
    try:
        index_info = await asyncio.wait_for(collection.index_information(), timeout=30)  # Увеличиваем таймаут до 30 секунд
    except asyncio.TimeoutError:
        print("Timeout occurred while fetching index information")
    if index_info and "email_1" not in index_info:
        await collection.create_index("email")

async def on_startup():
    global redis_client
    redis_client = aioredis.from_url(settings.BROKER_URL, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis_client), prefix="cache")
    await FastAPILimiter.init(redis_client)
    await create_indexes()

async def on_shutdown():
    global redis_client
    if redis_client:
        await redis_client.close()
