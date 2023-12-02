import json

import pytest
from aiohttp.web_response import Response, json_response
from pytest_mock import MockerFixture

from api.router.utils.method_interface import MethodInterface
from src.api.router.utils.base_view import BaseView


class FakeMethod(MethodInterface):
    def __init__(self, *args, **kwargs): pass

    async def prepare_request(self) -> bool: return True

    async def handle(self) -> bool: return True

    async def prepare_response(self) -> bool: return True

    @property
    def response(self) -> Response: return json_response(status=200, data={"key": "value"})

    @property
    def error(self) -> dict: return {}


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "post",
        "put",
        "delete"
    ]
)
@pytest.mark.asyncio
async def test_base_view(mocker: MockerFixture, method: str):
    mocker.patch.object(BaseView, f"_{method}_method", new=FakeMethod)
    base_view = BaseView(None)

    response = await base_view.__getattribute__(method)()
    assert response.status == 200, response.body
    assert response.body.decode() == json.dumps({"key": "value"})


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "post",
        "put",
        "delete"
    ]
)
@pytest.mark.asyncio
async def test_if_method_is_not_allowed(method: str):
    base_view = BaseView(None)

    response = await base_view.__getattribute__(method)()
    assert response.status == 405, response.body
    assert response.body.decode() == json.dumps({"status": 405, "errors": ["method is not allowed"]})
