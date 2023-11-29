from aiohttp.web import View, Request as AiohttpRequest

from src.api.interface import APIInterface


class Request(AiohttpRequest):

    @property
    def api(self) -> APIInterface:
        return super().app()


class BaseView(View):
    @property
    def request(self) -> Request:
        return super().request
