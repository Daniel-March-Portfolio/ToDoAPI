from aiohttp.web_routedef import RouteDef

from src.api.router.interface import RouterInterface
from src.api.router.login.setup import setup as setup_login_routes
from src.api.router.logout.setup import setup as setup_logout_routes
from src.api.router.register.setup import setup as setup_register_routes
from src.api.router.task.setup import setup as setup_task_routes
from src.api.router.tasks.setup import setup as setup_tasks_routes
from src.api.router.user.setup import setup as setup_user_routes


class Router(RouterInterface):
    __routes: list[RouteDef]

    def __init__(self):
        self.__routes = []
        self.__setup_routes()

    def __setup_routes(self):
        setup_login_routes(self)
        setup_logout_routes(self)
        setup_register_routes(self)
        setup_task_routes(self)
        setup_tasks_routes(self)
        setup_user_routes(self)

    def add_route(self, route: RouteDef) -> None:
        self.__routes.append(route)

    @property
    def routes(self) -> list[RouteDef]:
        return self.__routes
