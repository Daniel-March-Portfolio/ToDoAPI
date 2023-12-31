from dataclasses import dataclass
from json import JSONDecodeError
from uuid import UUID

from aiohttp.web_response import Response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.exceptions import APIException
from src.core.models import Task
from src.core.utils.create_condition import create_condition
from src.core.utils.get_user_by_session import get_user_by_session


@dataclass
class Data:
    uuid: UUID


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

        uuid_string = data.get("uuid")
        if uuid_string is None:
            self.__error = {"status": 400, "errors": ["uuid not found in request"]}
            return False
        if not isinstance(uuid_string, str):
            self.__error = {"status": 422, "errors": ["uuid is not a string"]}
            return False

        try:
            task_uuid = UUID(uuid_string)
        except (AttributeError, ValueError, TypeError):
            self.__error = {"status": 400, "errors": ["bad uuid"]}
            return False

        task = await Task.filter(create_condition(Task.uuid, task_uuid), engine=database_engine, fetch_one=True)
        if task is None:
            self.__error = {"status": 404, "errors": "task not found"}
            return False

        if task.user_uuid != user.uuid:
            self.__error = {"status": 404, "errors": "task not found"}
            return False

        self.__data = Data(uuid=task.uuid)

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.app.database_engine
        task = await Task.filter(create_condition(Task.uuid, self.__data.uuid), engine=database_engine, fetch_one=True)
        await task.delete(database_engine)
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
