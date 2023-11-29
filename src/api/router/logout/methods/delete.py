from dataclasses import dataclass

from aiohttp.web_response import Response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface


@dataclass
class Data:
    session: str


class Delete(MethodInterface):
    __request: Request
    __response: Response | None
    __data: Data | None
    __error: dict | None

    def __init__(self, request: Request):
        self.__request = request
        self.__response = None
        self.__data = None
        self.__error = None

    async def prepare_request(self) -> bool:
        session = self.__request.cookies.get("session")
        if session is None:
            self.__error = {"status": 400, "errors": ["session not found in cookies"]}
            return False
        self.__data = Data(
            session=session
        )
        return True

    async def handle(self) -> bool:
        await self.__request.api.redis.delete(self.__data.session)
        return True

    async def prepare_response(self) -> bool:
        self.__response = Response(status=204)
        return True

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def error(self) -> dict:
        return self.__error or {}
