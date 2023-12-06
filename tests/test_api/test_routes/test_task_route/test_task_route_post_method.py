import json
from typing import Any

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.task.methods import Post
from src.core.models import Task
from tests.data_classes import UserDataClass, TaskDataClass
from tests.test_api.data_classes import RequestDataClass
from tests.utils.create_user_and_session import create_user_and_session


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 0

    session = "some_session"
    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )

    method = Post(
        request=Request(
            app=api,
            raw_json={"title": normal_tasks[0].title},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is True, method.error

    prepare_response_successful = await method.prepare_response()
    assert prepare_response_successful is True, method.error

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1

    task = await Task.filter(engine=engine, fetch_one=True)

    assert isinstance(method.response, Response), method.response
    assert method.response.status == 201
    assert method.response.body is not None
    assert method.response.body.decode() == json.dumps({"uuid": task.uuid.hex}), method.response.body.decode()


@pytest.mark.asyncio
async def test_for_short_title(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    session = "some_session"
    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )
    method = Post(
        request=Request(
            app=api,
            raw_json={"title": ""},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 400, "errors": ["title is too short"]}


@pytest.mark.parametrize(
    "json_data",
    [
        [None],
        ["no_json"],
        [b"no_json"],
    ]
)
@pytest.mark.asyncio
async def test_for_bad_json_data(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], json_data: Any
):
    session = "some_session"
    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )
    method = Post(
        request=Request(
            app=api,
            raw_json=json_data,
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["body can not be parsed as json"]}, method.error


@pytest.mark.parametrize(
    "title",
    [1, True, [], None]
)
@pytest.mark.asyncio
async def test_for_wrong_fields_type(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], title: Any
):
    session = "some_session"
    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )
    method = Post(
        request=Request(
            app=api,
            raw_json={"title": title},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["title is not a string"]}, method.error
