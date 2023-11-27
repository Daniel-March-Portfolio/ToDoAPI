from aiohttp.web_routedef import view

from src.api.router.interface import RouterInterface
from src.api.router.urls import URLs
from src.api.router.register.handler import Handler


def setup(router: RouterInterface):
    router.add_route(view(URLs.register, Handler))
