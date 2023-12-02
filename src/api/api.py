import asyncio

from aiohttp.web import Application, TCPSite, AppRunner
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api.interface import APIInterface
from src.api.router import Router
from src.api.router.interface import RouterInterface
from src.api.state import State
from src.core.redis import RedisInterface
from src.env import EnvInterface


class API(Application, APIInterface):
    __env: EnvInterface
    __tcp_site: None | TCPSite
    __state: State
    __database_engine: AsyncEngine
    __redis: RedisInterface

    def __init__(
            self, env: EnvInterface, database_engine: AsyncEngine, redis: RedisInterface,
            router: RouterInterface | None = None
    ):
        router = router or Router()
        super().__init__()
        self.__env = env
        self.__database_engine = database_engine
        self.__redis = redis
        self.__tcp_site = None
        self.router.add_routes(router.routes)
        self.__state = State.INITIALIZED

    @property
    def state(self) -> State:
        return self.__state

    @property
    def redis(self) -> RedisInterface:
        return self.__redis

    @property
    def env(self) -> EnvInterface:
        return self.__env

    @property
    def database_engine(self) -> AsyncEngine:
        return self.__database_engine

    async def run(self) -> None:
        runner = AppRunner(self)
        await runner.setup()
        self.__tcp_site = TCPSite(runner, host=self.__env.api_host, port=self.__env.api_port)
        await self.__tcp_site.start()

        self.__state = State.RUNNING
        await self.__await_state(State.STOPPED)

    async def stop(self) -> None:
        self.__state = State.STOPPING
        await self.__tcp_site.stop()
        self.__tcp_site = None
        self.__state = State.STOPPED

    async def __await_state(self, state: State) -> None:
        while self.__state != state:
            await asyncio.sleep(0)
