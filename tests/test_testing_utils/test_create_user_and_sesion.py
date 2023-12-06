import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import APIInterface
from src.core.models import User
from tests.data_classes import UserDataClass
from tests.utils.create_user_and_session import create_user_and_session


@pytest.mark.asyncio
async def test_create_user_and_session(api: APIInterface, engine: AsyncEngine, normal_users: list[UserDataClass]):
    n_users = await User.get_count_of_rows(engine)
    assert n_users == 0

    session = "some_session"
    in_redis_session = await api.redis.get(session)
    assert in_redis_session is None

    await create_user_and_session(
        login=normal_users[0].login,
        name=normal_users[0].name,
        password_hash=normal_users[0].password_hash,
        engine=engine,
        redis=api.redis,
        session=session
    )

    n_users = await User.get_count_of_rows(engine)
    assert n_users == 1
    in_redis_session = await api.redis.get(session)
    assert in_redis_session is not None
