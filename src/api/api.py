import asyncio

from aiohttp.web import Application, TCPSite, AppRunner

from src.api.interface import APIInterface
from src.api.router import Router
from src.api.router.interface import RouterInterface
from src.api.state import State
from src.env import EnvInterface


class API(Application, APIInterface):
    __env: EnvInterface
    __tcp_site: None | TCPSite
    __state: State
    __router: RouterInterface

    def __init__(self, env: EnvInterface, router: RouterInterface):
        super().__init__()
        router = router or Router()
        self.__env = env
        self.__tcp_site = None
        self.add_routes(router.routes)
        self.__state = State.INITIALIZED

    @property
    def state(self) -> State:
        return self.__state

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
