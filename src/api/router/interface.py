from abc import ABC, abstractmethod

from aiohttp.web_routedef import RouteTableDef, RouteDef


class RouterInterface(ABC):
    @property
    @abstractmethod
    def routes(self) -> RouteTableDef: ...

    @abstractmethod
    def add_route(self, route: RouteDef) -> None: ...
