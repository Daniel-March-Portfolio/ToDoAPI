from typing import Any

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.task.methods import Put
from src.core.models import User, Task
from tests.data_classes import UserDataClass, TaskDataClass
from tests.test_api.data_classes import RequestDataClass


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    task = Task(
        title=normal_tasks[0].title,
        user_uuid=user.uuid
    )
    await task.save(engine)
    session = "some_session"
    await api.redis.set(session, user.uuid.hex)

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1

    method = Put(
        request=Request(
            api=api,
            raw_json={"uuid": task.uuid.hex, "new_title": normal_tasks[1].title},
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
    assert task.title == normal_tasks[1].title
    assert isinstance(method.response, Response), method.response
    assert method.response.status == 204
    assert method.response.body is None


@pytest.mark.asyncio
async def test_for_unauthorized_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):  # ToDo Deside what to do with this test because it is already tested in utils tests
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)

    method = Put(
        request=Request(
            api=api,
            raw_json={"uuid": normal_tasks[0].uuid.hex, "new_title": normal_tasks[1].title}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_expired_session(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):  # ToDo Deside what to do with this test because it is already tested in utils tests
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    session = "some_session"

    method = Put(
        request=Request(
            api=api,
            raw_json={"uuid": normal_tasks[0].uuid.hex, "new_title": normal_tasks[1].title},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_deleted_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):  # ToDo Deside what to do with this test because it is already tested in utils tests
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    session = "some_session"
    await api.redis.set(session, user.uuid.hex)
    await user.delete(engine)

    method = Put(
        request=Request(
            api=api,
            raw_json={"uuid": normal_tasks[0].uuid.hex, "new_title": normal_tasks[1].title},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_short_title(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    task = Task(
        title=normal_tasks[0].title,
        user_uuid=user.uuid
    )
    await task.save(engine)
    session = "some_session"
    await api.redis.set(session, user.uuid.hex)

    method = Put(
        request=Request(
            api=api,
            raw_json={"uuid": task.uuid.hex, "new_title": ""},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 400, "errors": ["new_title is too short"]}


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
    method = Put(
        request=Request(
            api=api,
            raw_json=json_data
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["body can not be parsed as json"]}, method.error
