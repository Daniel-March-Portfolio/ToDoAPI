import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.logout.methods import Delete
from tests.data_classes import UserDataClass
from tests.test_api.data_classes import RequestDataClass


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    await api.redis.set("some_session", "")

    method = Delete(
        request=Request(
            app=api,
            cookies={"session": "some_session"}
        ),
    )

    session_in_redis = await api.redis.get("some_session")
    assert session_in_redis is not None

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is True, method.error

    prepare_response_successful = await method.prepare_response()
    assert prepare_response_successful is True, method.error

    assert isinstance(method.response, Response), method.response
    assert method.response.body is None
    assert method.response.status == 204

    session_in_redis = await api.redis.get("some_session")
    assert session_in_redis is None


@pytest.mark.asyncio
async def test_for_empty_cookies(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    method = Delete(
        request=Request(
            app=api,
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False
    assert method.error == {"status": 400, "errors": ["session not found in cookies"]}
