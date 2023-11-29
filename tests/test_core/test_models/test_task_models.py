import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import Task, User
from tests.data_classes import TaskDataClass, UserDataClass


@pytest.mark.asyncio
async def test_create_task(engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    task = Task(
        title=normal_tasks[0].title,
        user=user,
    )
    assert task.uuid is None
    assert task.created_at is None

    n_tasks = await Task.get_count_of_rows(engine)
    n_users = await User.get_count_of_rows(engine)
    assert n_tasks == 0
    assert n_users == 0

    await task.save(engine)
    assert task.title == normal_tasks[0].title
    assert task.uuid is not None
    assert task.created_at is not None

    n_tasks = await Task.get_count_of_rows(engine)
    n_users = await User.get_count_of_rows(engine)
    assert n_tasks == 1
    assert n_users == 1

    database_tasks = await Task.get_all(engine=engine)
    database_task = database_tasks[0]
    assert database_task.uuid == task.uuid
    assert database_task.title == task.title
    assert database_task.created_at == task.created_at
    assert database_task.user_uuid == task.user_uuid


@pytest.mark.asyncio
async def test_update_task(engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    task = Task(
        title=normal_tasks[0].title,
        user=user,
    )

    await task.save(engine)

    task.title = normal_tasks[1].title
    database_tasks = await Task.get_all(engine=engine)
    database_task = database_tasks[0]
    assert database_task.title != task.title

    await task.save(engine)

    database_tasks = await Task.get_all(engine=engine)
    database_task = database_tasks[0]
    assert database_task.title == task.title


@pytest.mark.asyncio
async def test_delete_task(engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    task = Task(
        title=normal_tasks[0].title,
        user=user,
    )

    await task.save(engine)

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1

    await task.delete(engine)
    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 0
