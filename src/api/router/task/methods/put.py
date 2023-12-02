from dataclasses import dataclass
from uuid import UUID

from aiohttp.web_response import Response

from src.core.exceptions import APIException
from src.core.utils.create_condition import create_condition
from src.core.utils.get_user_by_session import get_user_by_session
from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import Task


@dataclass
class Data:
    user_uuid: UUID
    task_uuid: UUID
    title: str


class Put(MethodInterface):
    __request: Request
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
            data = await self.__request.json()
        except:  # ToDo add certain type
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        title = data.get("new_title")
        if title is None or len(title) < 5:
            self.__error = {"status": 400, "errors": ["new_title is too short"]}
            return False

        task_uuid_str = data.get("uuid")
        if task_uuid_str is None:
            self.__error = {"status": 400, "errors": ["uuid not found in request"]}
            return False

        try:
            task_uuid = UUID(task_uuid_str)
        except:
            self.__error = {"status": 400, "errors": ["bad uuid"]}
            return False

        try:
            user = await get_user_by_session(
                redis=self.__request.app.redis,
                database_engine=database_engine,
                session=self.__request.cookies.get("session")
            )
        except APIException as exception:
            self.__error = {"status": exception.status, "errors": exception.errors}
            return False

        task = await Task.filter(
            create_condition(Task.uuid, task_uuid),
            engine=database_engine,
            fetch_one=True
        )
        if task is None:
            self.__error = {"status": 404, "errors": ["task not found"]}
            return False

        self.__data = Data(
            user_uuid=user.uuid,
            title=title,
            task_uuid=task.uuid
        )

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.app.database_engine

        task = await Task.filter(
            create_condition(Task.uuid, self.__data.task_uuid),
            engine=database_engine,
            fetch_one=True
        )
        task.title = self.__data.title
        await task.save(database_engine)

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
