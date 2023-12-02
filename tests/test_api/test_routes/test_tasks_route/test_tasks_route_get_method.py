import json

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.utils.create_condition import create_condition
from src.api import APIInterface
from src.api.router.tasks.methods import Get
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
    await Task(
        title=normal_tasks[0].title,
        user_uuid=user.uuid
    ).save(engine)
    await Task(
        title=normal_tasks[1].title,
        user_uuid=user.uuid
    ).save(engine)

    session = "some_session"
    await api.redis.set(session, user.uuid.hex)

    method = Get(
        request=Request(
            api=api,
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is True, method.error

    handle_successful = await method.handle()
    assert handle_successful is True, method.error

    prepare_response_successful = await method.prepare_response()
    assert prepare_response_successful is True, method.error

    assert isinstance(method.response, Response), method.response
    assert method.response.status == 200

    got = json.loads(method.response.body.decode())
    assert "tasks" in got, got

    got = [task["uuid"] for task in got["tasks"]]
    expected = [task.uuid.hex for task in await Task.filter(create_condition(Task.user_uuid, user.uuid), engine=engine)]
    assert set(got) == set(expected)


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

    method = Get(
        request=Request(
            api=api,
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

    method = Get(
        request=Request(
            api=api,
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

    method = Get(
        request=Request(
            api=api,
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}
