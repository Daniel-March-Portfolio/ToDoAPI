from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncEngine

from core.redis import RedisInterface
from src.api import API
from src.api import APIInterface
from src.env.interface import EnvInterface


class FakeEnv(EnvInterface):
    @property
    def database_url(self) -> str:
        return "sqlite+aiosqlite://"

    @property
    def redis_host(self) -> str:
        return "127.0.0.1"

    @property
    def redis_port(self) -> int:
        return 8765

    @property
    def api_host(self) -> str:
        return "127.0.0.1"

    @property
    def api_port(self) -> int:
        return 8000

    @property
    def api_session_ttl(self) -> int:
        return 100

    @property
    def api_salt(self) -> str:
        return "some_salt"


@fixture(scope="function")
def api(engine: AsyncEngine, redis: RedisInterface) -> APIInterface:
    env = FakeEnv()
    api = API(
        env=env,
        database_engine=engine,
        redis=redis
    )
    return api
