from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncEngine

from src.api.state import State
from src.core.redis import RedisInterface
from src.env import EnvInterface


class APIInterface(ABC):
    @property
    @abstractmethod
    def state(self) -> State: ...

    @property
    @abstractmethod
    def redis(self) -> RedisInterface: ...

    @property
    @abstractmethod
    def env(self) -> EnvInterface: ...

    @property
    @abstractmethod
    def database_engine(self) -> AsyncEngine: ...

    @abstractmethod
    def run(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
