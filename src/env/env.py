import os

from src.core.exceptions import CoreException
from src.env.interface import EnvInterface


class Env(EnvInterface):
    __database_url: str
    __api_host: str
    __api_port: int
    __api_session_ttl: int
    __api_salt: str
    __redis_host: str
    __redis_port: int

    def __init__(self):
        database_url: str | None = os.getenv("DATABASE_URL")
        api_host: str | None = os.getenv("API_HOST")
        api_port: str | None = os.getenv("API_PORT")
        api_session_ttl: str | None = os.getenv("API_SESSION_TTL")
        api_salt: str | None = os.getenv("API_SALT")
        redis_host: str | None = os.getenv("REDIS_HOST")
        redis_port: str | None = os.getenv("REDIS_PORT")

        errors: list[str] = []
        if database_url is None:
            errors.append("DATABASE_URL not found in environ variables")

        if api_host is None:
            errors.append("API_HOST not found in environ variables")

        if api_port is None:
            errors.append("API_PORT not found in environ variables")
        elif not api_port.isdecimal():
            errors.append("API_PORT is not an integer")

        if api_session_ttl is None:
            errors.append("API_SESSION_TTL not found in environ variables")
        elif not api_session_ttl.isdecimal():
            errors.append("API_SESSION_TTL is not an integer")

        if api_salt is None:
            errors.append("API_SALT not found in environ variables")

        if redis_host is None:
            errors.append("REDIS_HOST not found in environ variables")

        if redis_port is None:
            errors.append("REDIS_PORT not found in environ variables")
        elif not redis_port.isdecimal():
            errors.append("REDIS_PORT is not an integer")

        if errors:
            raise CoreException(errors=errors)

        self.__database_url = database_url
        self.__api_host = api_host
        self.__api_port = int(api_port)
        self.__api_session_ttl = int(api_session_ttl)
        self.__api_salt = api_salt
        self.__redis_host = redis_host
        self.__redis_port = int(redis_port)

    @property
    def database_url(self) -> str:
        return self.__database_url

    @property
    def api_host(self) -> str:
        return self.__api_host

    @property
    def api_port(self) -> int:
        return self.__api_port

    @property
    def api_session_ttl(self) -> int:
        return self.__api_session_ttl

    @property
    def api_salt(self) -> str:
        return self.__api_salt

    @property
    def redis_host(self) -> str:
        return self.__redis_host

    @property
    def redis_port(self) -> int:
        return self.__redis_port

