import json

import pytest
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.tasks.methods import Get
from src.core.models import Task
from src.core.utils.create_condition import create_condition
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
    await Task(
        title=normal_tasks[0].title,
        user_uuid=user.uuid
    ).save(engine)
    await Task(
        title=normal_tasks[1].title,
        user_uuid=user.uuid
    ).save(engine)

    method = Get(
        request=Request(
            app=api,
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
