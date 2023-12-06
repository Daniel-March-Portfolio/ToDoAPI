from abc import ABC

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.api.router.task.methods import Delete as TaskDelete
from src.api.router.task.methods import Get as TaskGet
from src.api.router.task.methods import Post as TaskPost
from src.api.router.task.methods import Put as TaskPut
from src.api.router.tasks.methods import Delete as TasksDelete
from src.api.router.tasks.methods import Get as TasksGet
from src.api.router.utils.method_interface import MethodInterface
from src.core.models import User
from tests.data_classes import UserDataClass, TaskDataClass
from tests.test_api.data_classes import RequestDataClass
from utils.create_user_and_session import create_user_and_session


class Request(RequestDataClass):
    pass


class FakeMethodInterface(MethodInterface, ABC):
    def __init__(self, request):
        pass


@pytest.mark.parametrize(
    "method",
    [TasksGet, TasksDelete, TaskPut, TaskPost, TaskGet, TaskDelete]
)
@pytest.mark.asyncio
async def test_for_unauthorized_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass],
        method: type[FakeMethodInterface]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)

    method = method(
        request=Request(
            app=api
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.parametrize(
    "method",
    [TasksGet, TasksDelete, TaskPut, TaskPost, TaskGet, TaskDelete]
)
@pytest.mark.asyncio
async def test_for_expired_session(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass],
        method: type[FakeMethodInterface]
):
    user = User(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash
    )
    await user.save(engine)
    session = "some_session"

    method = method(
        request=Request(
            app=api,
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}


@pytest.mark.parametrize(
    "method",
    [TasksGet, TasksDelete, TaskPut, TaskPost, TaskGet, TaskDelete]
)
@pytest.mark.asyncio
async def test_for_deleted_user(
        api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass],
        method: type[FakeMethodInterface]
):
    session = "some_session"
    user = await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash, session=session,
        engine=engine,
        redis=api.redis
    )
    await user.delete(engine)

    method = method(
        request=Request(
            app=api,
            cookies={"session": session}
        ),
    )

    prepare_request_successful = await method.prepare_request()
    assert prepare_request_successful is False

    assert method.error == {"status": 403, "errors": ["bad session"]}
