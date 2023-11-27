from aiohttp.web_routedef import view

from src.api.router.interface import RouterInterface
from src.api.router.urls import URLs
from src.api.router.user.handler import Handler


def setup(router: RouterInterface):
    router.add_route(view(URLs.user, Handler))
