from dataclasses import dataclass
from uuid import UUID

from aiohttp.web_response import Response, json_response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import User, Task
from src.core.utils.create_condition import create_condition


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
        database_engine = self.__request.api.database_engine
        try:
            data = await self.__request.json()
        except:  # ToDo add certain type
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        title = data.get("title")
        if title is None or len(title) < 5:
            self.__error = {"status": 400, "errors": ["title is too short"]}
            return False

        session = self.__request.cookies.get("session")
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

        self.__data = Data(
            user_uuid=user.uuid,
            title=title
        )

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.api.database_engine

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
