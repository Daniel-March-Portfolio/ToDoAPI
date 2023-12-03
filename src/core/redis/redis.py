from redis.asyncio import Redis as _Redis

from src.core.redis.interface import RedisInterface


class Redis(_Redis, RedisInterface):
    def __new__(cls, *args, url: str = None, **kwargs) -> "Redis":
        if url is not None:
            return cls.from_url(url=url)
        return _Redis(*args, **kwargs)
