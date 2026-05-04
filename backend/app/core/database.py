import asyncpg
import motor.motor_asyncio
import redis.asyncio as aioredis
from app.core.config import settings

_pg_pool = None
_mongo_client = None
_redis_client = None

async def get_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = await asyncpg.create_pool(settings.postgres_url, min_size=2, max_size=10)
    return _pg_pool

def get_mongo():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
    return _mongo_client["ims_db"]

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client
