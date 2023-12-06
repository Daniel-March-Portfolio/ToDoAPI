from typing import Any

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.register.methods import Post
from src.core.models import User
from tests.data_classes import UserDataClass
from tests.test_api.data_classes import RequestDataClass


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0
    method = Post(
        request=Request(
            app=api,
            raw_json={
                "name": normal_users[0].name,
                "login": normal_users[0].login,
                "password": normal_users[0].password
            }
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is True, method.error

    prepare_response_successful = await method.prepare_response()
    assert prepare_response_successful is True, method.error

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1

    assert isinstance(method.response, Response), method.response
    assert method.response.body is None
    assert method.response.status == 201


@pytest.mark.parametrize(
    "name,login,password",
    [
        [1, 1, 1],
        [True, True, True],
        [[], [], []],
        [None, None, None]
    ]
)
@pytest.mark.asyncio
async def test_wrong_fields_type(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass],
        name: str | None, login: str | None, password: str | None
):
    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0
    method = Post(
        request=Request(
            app=api,
            raw_json={
                "name": name,
                "login": login,
                "password": password
            }
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False, method.error

    expected = {"status": 400, "errors": ["name is not a string", "login is not a string", "password is not a string"]}
    assert method.error == expected, method.error

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0


@pytest.mark.asyncio
async def test_if_login_already_in_use(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    await User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    ).save(engine)

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1

    method = Post(
        request=Request(
            app=api,
            raw_json={
                "name": normal_users[0].name,
                "login": normal_users[0].login,
                "password": normal_users[0].password
            }
        ),
    )

    assert (await method.prepare_request()) is True

    handle_successful = await method.handle()
    assert handle_successful is False, method.error

    assert method.error == {"status": 409, "errors": ["login already in use"]}, method.error

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1


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
            app=api,
            raw_json=json_data
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["body can not be parsed as json"]}, method.error
