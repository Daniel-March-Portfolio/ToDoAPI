import datetime
from uuid import UUID

from pytest_asyncio import fixture

from src.core.utils.hash_password import hash_password
from tests.test_core.data_classes import UserDataClass, TaskDataClass


@fixture(scope="session")
def normal_users() -> list[UserDataClass]:
    users = [
        UserDataClass(
            uuid=UUID('342faa8e-3b29-41d4-9ac0-69d95e043776'),
            name="First User",
            login="first_login",
            password_hash=hash_password(password="password", login="first_login", salt="some_salt"),
            created_at=datetime.datetime(year=2023, month=1, day=1),
        ),
        UserDataClass(
            uuid=UUID('779b2125-9131-46bb-b9dc-2d91624daca4'),
            name="Second User",
            login="second_login",
            password_hash=hash_password(password="password", login="second_login", salt="some_salt"),
            created_at=datetime.datetime(year=2023, month=2, day=2),
        ),
        UserDataClass(
            uuid=UUID('3e81ac97-d764-4738-b85f-ce9c40b701e9'),
            name="Third User",
            login="third_login",
            password_hash=hash_password(password="password", login="third_login", salt="some_salt"),
            created_at=datetime.datetime(year=2023, month=3, day=3),
        ),
    ]
    return users


@fixture(scope="session")
def normal_tasks() -> list[TaskDataClass]:
    users = [
        TaskDataClass(
            uuid=UUID('342faa8e-3b29-41d4-9ac0-69d95e043776'),
            title="First task",
            created_at=datetime.datetime(year=2023, month=4, day=4)
        ),
        TaskDataClass(
            uuid=UUID('779b2125-9131-46bb-b9dc-2d91624daca4'),
            title="Second task",
            created_at=datetime.datetime(year=2023, month=5, day=5)
        ),
        TaskDataClass(
            uuid=UUID('3e81ac97-d764-4738-b85f-ce9c40b701e9'),
            title="Third task",
            created_at=datetime.datetime(year=2023, month=6, day=6)
        ),
    ]
    return users
