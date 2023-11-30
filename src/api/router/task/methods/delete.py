from dataclasses import dataclass
from uuid import UUID

from aiohttp.web_response import Response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import User, Task
from src.core.utils.create_condition import create_condition


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
        database_engine = self.__request.api.database_engine
        try:
            data = await self.__request.json()
        except:  # ToDo add certain type
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        uuid_string = data.get("uuid")
        if uuid_string is None:
            self.__error = {"status": 400, "errors": ["uuid not found in request"]}
            return False
        try:
            task_uuid = UUID(uuid_string)
        except:
            self.__error = {"status": 400, "errors": ["bad uuid"]}
            return False

        session = self.__request.cookies.get("session")  # ToDo write util to check authorization
        if session is None:
            self.__error = {"status": 403, "errors": "bad session"}
            return False

        bytes_user_uuid_by_session_in_redis: bytes | None = await self.__request.api.redis.get(session)
        if bytes_user_uuid_by_session_in_redis is None:
            self.__error = {"status": 403, "errors": "bad session"}
            return False

        user_uuid_by_session_in_redis = UUID(bytes_user_uuid_by_session_in_redis.decode())
        user = await User.filter(
            create_condition(User.uuid, user_uuid_by_session_in_redis),
            engine=database_engine,
            fetch_one=True

        )
        if user is None:
            self.__error = {"status": 403, "errors": "bad session"}
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
        database_engine = self.__request.api.database_engine
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
