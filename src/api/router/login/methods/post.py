import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from aiohttp.web_response import Response

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import User
from src.core.utils.create_condition import create_condition, OPERATOR
from src.core.utils.hash_password import hash_password


@dataclass
class Data:
    login: str
    password: str


@dataclass
class Result:
    session: str


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
        prepare_errors: list[str] = []
        try:
            data = await self.__request.json()
        except:  # ToDo add certain type
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        login = data.get("login")
        password = data.get("password")
        if login is None or len(login) == 0:
            prepare_errors.append("empty login")
        if password is None or len(password) == 0:
            prepare_errors.append("empty password")
        if prepare_errors:
            self.__error = {"status": 400, "errors": prepare_errors}
            return False

        self.__data = Data(
            login=login,
            password=password
        )

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.api.database_engine

        user = await User.filter(
            create_condition(User.login, self.__data.login, OPERATOR.EQUAL),
            fetch_one=True,
            engine=database_engine
        )
        if user is None:
            self.__error = {"status": 403, "errors": ["bad login or password"]}
            return False

        password_hash = hash_password(self.__data.password, self.__data.login, self.__request.api.env.api_salt)
        if user.password_hash != password_hash:
            self.__error = {"status": 403, "errors": ["bad login or password"]}
            return False

        session = ".".join([user.uuid.hex, uuid.uuid4().hex])
        await self.__request.api.redis.set(session, "", ex=self.__request.api.env.api_session_ttl)
        self.__result = Result(session=session)
        return True

    async def prepare_response(self) -> bool:
        session_expires = datetime.utcnow() + timedelta(seconds=self.__request.api.env.api_session_ttl)
        session_expires = session_expires.strftime("%a, %d %b %Y %H:%M:00 UTC")
        self.__response = Response(
            status=200,
            headers={
                "Set-Cookie": f"session={self.__result.session}; SameSite=Strict; Expires={session_expires}; Secure; HttpOnly"
            }
        )
        return True

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def error(self) -> dict:
        return self.__error or {}
