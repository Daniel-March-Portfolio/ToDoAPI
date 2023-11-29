from abc import ABC, abstractmethod

from redis.commands.core import ResponseT
from redis.typing import PatternT, KeyT, EncodableT


class RedisInterface(ABC):
    @abstractmethod
    def get(self, name: KeyT) -> ResponseT: ...

    @abstractmethod
    def set(self, name: KeyT, value: EncodableT, ex: int = None, ) -> ResponseT: ...

    @abstractmethod
    def keys(self, pattern: PatternT = "*", *kwargs) -> ResponseT: ...
