from redis.asyncio import Redis as _Redis

from src.core.redis.interface import RedisInterface


class Redis(_Redis, RedisInterface):
    pass
