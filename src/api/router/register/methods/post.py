from dataclasses import dataclass

from aiohttp.web_response import Response
from sqlalchemy.exc import IntegrityError

from src.api.router.utils.base_view import Request
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import User
from src.core.utils.hash_password import hash_password


@dataclass
class Data:
    name: str
    login: str
    password: str


class Post(MethodInterface):
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
        prepare_errors: list[str] = []
        try:
            data = await self.__request.json()
        except:  # ToDo add certain type
            self.__error = {"status": 422, "errors": ["body can not be parsed as json"]}
            return False

        name = data.get("name")
        login = data.get("login")
        password = data.get("password")
        if name is None or len(name) < 2:
            prepare_errors.append("name is too short")
        if login is None or len(login) < 5:
            prepare_errors.append("login is too short")
        if password is None or len(password) < 5:
            prepare_errors.append("password is too short")
        if prepare_errors:
            self.__error = {"status": 400, "errors": prepare_errors}
            return False

        self.__data = Data(
            name=name,
            login=login,
            password=password,
        )

        return True

    async def handle(self) -> bool:
        database_engine = self.__request.app.database_engine

        password_hash = hash_password(self.__data.password, self.__data.login, self.__request.app.env.api_salt)
        try:
            await User(
                name=self.__data.name,
                login=self.__data.login,
                password_hash=password_hash
            ).save(engine=database_engine)
        except IntegrityError:
            self.__error = {"status": 409, "errors": ["login already in use"]}
            return False

        return True

    async def prepare_response(self) -> bool:
        self.__response = Response(status=201)
        return True

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def error(self) -> dict:
        return self.__error or {}
