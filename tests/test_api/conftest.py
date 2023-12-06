from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.redis import RedisInterface
from tests.enum_classes import EnvVarEnumClass
from src.api import API
from src.api import APIInterface
from src.env.interface import EnvInterface


class FakeEnv(EnvInterface):
    @property
    def database_url(self) -> str:
        return EnvVarEnumClass.DATABASE_URL.value

    @property
    def redis_url(self) -> str:
        return EnvVarEnumClass.REDIS_URL.value

    @property
    def api_host(self) -> str:
        return EnvVarEnumClass.API_HOST.value

    @property
    def api_port(self) -> int:
        return EnvVarEnumClass.API_PORT.value

    @property
    def api_session_ttl(self) -> int:
        return EnvVarEnumClass.API_SESSION_TTL.value

    @property
    def api_salt(self) -> str:
        return EnvVarEnumClass.API_SALT.value


@fixture(scope="function")
async def api(engine: AsyncEngine, redis: RedisInterface) -> APIInterface:
    env = FakeEnv()
    api = API(
        env=env,
        database_engine=engine,
        redis=redis
    )
    return api
