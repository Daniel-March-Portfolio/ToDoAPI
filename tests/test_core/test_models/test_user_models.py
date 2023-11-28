import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import User
from tests.test_core.data_classes import UserDataClass


@pytest.mark.asyncio
async def test_create_user(engine: AsyncEngine, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    assert user.uuid is None
    assert user.created_at is None

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0

    await user.save(engine)
    assert user.name == normal_users[0].name
    assert user.login == normal_users[0].login
    assert user.password_hash == normal_users[0].password_hash
    assert user.uuid is not None
    assert user.created_at is not None

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1

    database_users = await User.get_all(engine=engine)
    database_user = database_users[0]
    assert database_user.name == user.name
    assert database_user.login == user.login
    assert database_user.password_hash == user.password_hash
    assert database_user.uuid == user.uuid
    assert database_user.created_at == user.created_at


@pytest.mark.asyncio
async def test_update_user(engine: AsyncEngine, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )

    await user.save(engine)

    user.name = normal_users[1].name
    user.login = normal_users[1].login
    user.password_hash = normal_users[1].password_hash
    database_users = await User.get_all(engine=engine)
    database_user = database_users[0]
    assert database_user.name != user.name
    assert database_user.login != user.login
    assert database_user.password_hash != user.password_hash

    await user.save(engine)

    database_users = await User.get_all(engine=engine)
    database_user = database_users[0]
    assert database_user.name == user.name
    assert database_user.login == user.login
    assert database_user.password_hash == user.password_hash


@pytest.mark.asyncio
async def test_delete_user(engine: AsyncEngine, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )

    await user.save(engine)

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1

    await user.delete(engine)
    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0
