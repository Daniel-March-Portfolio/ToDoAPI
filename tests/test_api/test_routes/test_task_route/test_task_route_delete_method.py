from typing import Any
from uuid import uuid4

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.task.methods import Delete
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

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": task.uuid.hex},
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
    assert n_tasks == 0

    assert isinstance(method.response, Response), method.response
    assert method.response.status == 204
    assert method.response.body is None


@pytest.mark.asyncio
async def test_for_unauthorized_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": uuid4().hex}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_expired_session(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    session = "some_session"

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": uuid4().hex},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_deleted_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    session = "some_session"
    await api.redis.set(session, user.uuid.hex)
    await user.delete(engine)

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": uuid4().hex},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.asyncio
async def test_for_empty_body(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    method = Delete(
        request=Request(
            api=api,
            raw_json={}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 400, "errors": ["uuid not found in request"]}


@pytest.mark.asyncio
async def test_if_task_does_not_exists(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)

    session = "some_session"
    await api.redis.set(session, user.uuid.hex)

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": uuid4().hex},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 404, "errors": "task not found"}


@pytest.mark.asyncio
async def test_if_try_to_delete_another_user_task(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user_1 = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user_1.save(engine)
    user_2 = User(
        login=normal_users[1].login,
        name=normal_users[1].name,
        password_hash=normal_users[1].password_hash
    )
    await user_2.save(engine)
    task = Task(
        title=normal_tasks[0].title,
        user_uuid=user_2.uuid
    )
    await task.save(engine)

    session = "some_session"
    await api.redis.set(session, user_1.uuid.hex)

    method = Delete(
        request=Request(
            api=api,
            raw_json={"uuid": task.uuid.hex},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 404, "errors": "task not found"}

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1


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
    method = Delete(
        request=Request(
            api=api,
            raw_json=json_data
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["body can not be parsed as json"]}, method.error
