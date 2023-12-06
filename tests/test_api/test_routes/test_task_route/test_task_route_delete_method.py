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
from tests.utils.create_user_and_session import create_user_and_session


class Request(RequestDataClass):
    pass


@pytest.mark.asyncio
async def test_method(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    session = "some_session"
    user = await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )
    task = Task(
        title=normal_tasks[0].title,
        user_uuid=user.uuid
    )
    await task.save(engine)

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1

    method = Delete(
        request=Request(
            app=api,
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
async def test_for_empty_body(
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

    method = Delete(
        request=Request(
            app=api,
            raw_json={},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 400, "errors": ["uuid not found in request"]}


@pytest.mark.asyncio
async def test_if_task_does_not_exists(
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

    method = Delete(
        request=Request(
            app=api,
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
    session = "some_session"
    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        session=session,
        engine=engine,
        redis=api.redis
    )
    another_user = User(
        login=normal_users[1].login,
        name=normal_users[1].name,
        password_hash=normal_users[1].password_hash
    )
    await another_user.save(engine)
    task = Task(
        title=normal_tasks[0].title,
        user_uuid=another_user.uuid
    )
    await task.save(engine)

    method = Delete(
        request=Request(
            app=api,
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
    method = Delete(
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
    "uuid",
    [1, True, []]
)
@pytest.mark.asyncio
async def test_for_wrong_fields_type(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], uuid: Any
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
    method = Delete(
        request=Request(
            app=api,
            raw_json={"uuid": uuid},
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 422, "errors": ["uuid is not a string"]}, method.error
