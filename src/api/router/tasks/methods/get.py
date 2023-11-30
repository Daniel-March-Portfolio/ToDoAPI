from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from aiohttp.web_response import Response, json_response

from core.exceptions import APIException
from core.utils.get_user_by_session import get_user_by_session
from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import Task
from src.core.utils.create_condition import create_condition


@dataclass
class Data:
    user_uuid: UUID


@dataclass
class Result:
    tasks: Sequence[Task]


class Get(MethodInterface):
    __request: Request
    __response: Response | None
    __result: Result | None
    __data: Data | None
    __error: dict | None

    def __init__(self, request: Request):
        self.__request = request
        self.__response = None
        self.__data = None
        self.__error = None

    async def prepare_request(self) -> bool:
        database_engine = self.__request.api.database_engine

        try:
            user = await get_user_by_session(
                redis=self.__request.api.redis,
                database_engine=database_engine,
                session=self.__request.cookies.get("session")
            )
        except APIException as exception:
            self.__error = {"status": exception.status, "errors": exception.errors}
            return False

        self.__data = Data(user_uuid=user.uuid)

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.api.database_engine
        tasks = await Task.filter(
            create_condition(Task.user_uuid, self.__data.user_uuid),
            order_by=[Task.created_at],
            engine=database_engine
        )
        self.__result = Result(
            tasks=tasks
        )
        return True

    async def prepare_response(self) -> bool:
        self.__response = json_response(
            {
                "tasks": [
                    {
                        "uuid": task.uuid.hex,
                        "title": task.title,
                        "created_at": task.created_at.isoformat()
                    } for task in self.__result.tasks
                ]
            },
            status=200
        )
        return True

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def error(self) -> dict:
        return self.__error or {}
