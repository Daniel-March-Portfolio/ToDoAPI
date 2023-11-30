import re
from typing import Any

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.login.methods import Post
from src.core.models import User
from tests.data_classes import UserDataClass
from tests.test_api.data_classes import RequestDataClass


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    await User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    ).save(engine)
    method = Post(
        request=Request(
            api=api,
            raw_json={"login": normal_users[0].login, "password": normal_users[0].password}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is True, method.error

    prepare_response_successful = await method.prepare_response()
    assert prepare_response_successful is True, method.error

    assert isinstance(method.response, Response), method.response
    assert method.response.body is None
    assert method.response.status == 200
    assert method.response.headers.get("Set-Cookie") is not None, method.response.headers.items()


@pytest.mark.asyncio
async def test_if_user_with_requested_login_does_not_exists(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]
):
    method = Post(
        request=Request(
            api=api,
            raw_json={"login": normal_users[0].login, "password": normal_users[0].password}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is False

    assert method.error == {"status": 403, "errors": ["bad login or password"]}


@pytest.mark.asyncio
async def test_for_wrong_password(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]
):
    await User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    ).save(engine)
    method = Post(
        request=Request(
            api=api,
            raw_json={"login": normal_users[0].login, "password": normal_users[1].password}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is False

    assert method.error == {"status": 403, "errors": ["bad login or password"]}


@pytest.mark.asyncio
async def test_for_empty_login_and_password(api: APIInterface, engine: AsyncEngine):
    method = Post(
        request=Request(
            api=api
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 400, "errors": ["empty login", "empty password"]}, method.error


@pytest.mark.parametrize(
    "json_data",
    [
        [None],
        ["no_json"],
        [b"no_json"],
    ]
)
@pytest.mark.asyncio
async def test_for_bad_json_data(api: APIInterface, engine: AsyncEngine, json_data: Any):
    method = Post(
        request=Request(
            api=api,
            raw_json=json_data
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["body can not be parsed as json"]}, method.error


@pytest.mark.asyncio
async def test_cookies(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)

    method = Post(
        request=Request(
            api=api,
            raw_json={"login": normal_users[0].login, "password": normal_users[0].password}
        ),
    )

    assert (await method.prepare_request()) is True
    assert (await method.handle()) is True
    assert (await method.prepare_response()) is True

    cookies = method.response.headers.get("Set-Cookie")
    assert cookies is not None

    pattern = re.compile(r"^session=.*; SameSite=Strict; Expires=.*; Secure; HttpOnly$")
    assert re.match(pattern, cookies) is not None, cookies

    session = cookies.split(";")[0][8:]
    bytes_user_uuid_by_session_in_redis: bytes = await api.redis.get(session)
    user_uuid_by_session_in_redis = bytes_user_uuid_by_session_in_redis.decode()
    assert user_uuid_by_session_in_redis == user.uuid.hex
