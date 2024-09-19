import os
import redis.asyncio as aioredis

redis_client = None

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}"
        )
    return redis_client
