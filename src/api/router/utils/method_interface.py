from abc import ABC, abstractmethod
from aiohttp.web_response import Response


class MethodInterface(ABC):
    @abstractmethod
    async def prepare_request(self) -> bool: ...

    @abstractmethod
    async def handle(self) -> bool: ...

    @abstractmethod
    async def prepare_response(self) -> bool: ...

    @property
    @abstractmethod
    def response(self) -> Response: ...

    @property
    @abstractmethod
    def error(self) -> dict: ...
