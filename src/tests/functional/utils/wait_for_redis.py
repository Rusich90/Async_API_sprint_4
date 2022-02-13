import aioredis
import asyncio


async def wait_redis():
    redis = await aioredis.create_redis(('redis', 6379))
    await redis.ping()
    redis.close()


if __name__ == '__main__':
    asyncio.run(wait_redis())
