from typing import Callable

from aiohttp.web import View, Request as AiohttpRequest
from aiohttp.web_response import json_response

from src.api.interface import APIInterface
from src.api.router.utils.method_interface import MethodInterface


class Request(AiohttpRequest):

    @property
    def app(self) -> APIInterface:
        return super().app()


class BaseView(View):
    _get_method: Callable[[Request], MethodInterface] | None = None
    _post_method: Callable[[Request], MethodInterface] | None = None
    _put_method: Callable[[Request], MethodInterface] | None = None
    _delete_method: Callable[[Request], MethodInterface] | None = None

    @property
    def request(self) -> Request:
        return super().request

    async def get(self):
        if self._get_method is None:
            return json_response(status=405, data={"status": 405, "errors": ["method is not allowed"]})
        method = self._get_method(self.request)

        prepare_request_successful = await method.prepare_request()
        if not prepare_request_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        handle_successful = await method.handle()
        if not handle_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        prepare_response_successful = await method.prepare_response()
        if not prepare_response_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        return method.response

    async def post(self):
        if self._post_method is None:
            return json_response(status=405, data={"status": 405, "errors": ["method is not allowed"]})
        method = self._post_method(self.request)

        prepare_request_successful = await method.prepare_request()
        if not prepare_request_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        handle_successful = await method.handle()
        if not handle_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        prepare_response_successful = await method.prepare_response()
        if not prepare_response_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        return method.response

    async def put(self):
        if self._put_method is None:
            return json_response(status=405, data={"status": 405, "errors": ["method is not allowed"]})
        method = self._put_method(self.request)

        prepare_request_successful = await method.prepare_request()
        if not prepare_request_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        handle_successful = await method.handle()
        if not handle_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        prepare_response_successful = await method.prepare_response()
        if not prepare_response_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        return method.response

    async def delete(self):
        if self._delete_method is None:
            return json_response(status=405, data={"status": 405, "errors": ["method is not allowed"]})
        method = self._delete_method(self.request)

        prepare_request_successful = await method.prepare_request()
        if not prepare_request_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        handle_successful = await method.handle()
        if not handle_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        prepare_response_successful = await method.prepare_response()
        if not prepare_response_successful:
            return json_response(status=method.error.get("status"), data=method.error)

        return method.response
