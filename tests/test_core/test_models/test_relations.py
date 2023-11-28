import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import Task, User
from tests.test_core.data_classes import TaskDataClass, UserDataClass


@pytest.mark.asyncio
async def test_tasks_cascade_deleting(
        engine: AsyncEngine, normal_users: list[UserDataClass], normal_tasks: list[TaskDataClass]
):
    user_1 = User(name=normal_users[0].name, login=normal_users[0].login, password_hash=normal_users[0].password_hash)
    user_2 = User(name=normal_users[1].name, login=normal_users[1].login, password_hash=normal_users[1].password_hash)
    await Task(title=normal_tasks[0].title, user=user_1).save(engine)
    await Task(title=normal_tasks[1].title, user=user_1).save(engine)
    await Task(title=normal_tasks[2].title, user=user_2).save(engine)

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 3

    await user_1.delete(engine)

    n_tasks = await Task.get_count_of_rows(engine)
    assert n_tasks == 1
