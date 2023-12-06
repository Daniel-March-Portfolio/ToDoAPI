from dataclasses import dataclass
from json import JSONDecodeError
from uuid import UUID

from aiohttp.web_response import Response, json_response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.exceptions import APIException
from src.core.models import Task
from src.core.utils.get_user_by_session import get_user_by_session


@dataclass
class Data:
    user_uuid: UUID
    title: str


@dataclass
class Result:
    uuid: UUID


class Post(MethodInterface):
    __request: Request
    __result: Result | None
    __response: Response | None
    __data: Data | None
    __error: dict | None

    def __init__(self, request: Request):
        self.__request = request
        self.__result = None
        self.__response = None
        self.__data = None
        self.__error = None

    async def prepare_request(self) -> bool:
        database_engine = self.__request.app.database_engine

        try:
            user = await get_user_by_session(
                redis=self.__request.app.redis,
                database_engine=database_engine,
                session=self.__request.cookies.get("session")
            )
        except APIException as exception:
            self.__error = {"status": exception.status, "errors": exception.errors}
            return False

        try:
            data = await self.__request.json()
        except (TypeError, JSONDecodeError):
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        title = data.get("title")
        if not isinstance(title, str):
            self.__error = {"status": 422, "errors": ["title is not a string"]}
            return False
        if title is None or len(title) < 5:
            self.__error = {"status": 400, "errors": ["title is too short"]}
            return False

        self.__data = Data(
            user_uuid=user.uuid,
            title=title
        )

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.app.database_engine

        task = Task(
            title=self.__data.title,
            user_uuid=self.__data.user_uuid
        )
        await task.save(database_engine)

        self.__result = Result(uuid=task.uuid)

        return True

    async def prepare_response(self) -> bool:
        self.__response = json_response(
            {"uuid": self.__result.uuid.hex},
            status=201
        )
        return True

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def error(self) -> dict:
        return self.__error or {}
