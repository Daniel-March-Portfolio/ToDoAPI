import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from core.exceptions import APIException
from core.models import User
from core.redis import RedisInterface
from data_classes import UserDataClass
from src.core.utils.get_user_by_session import get_user_by_session


@pytest.mark.asyncio
async def test_get_user_by_session(engine: AsyncEngine, redis: RedisInterface, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    await user.save(engine)
    session = "some_session"
    await redis.set(session, user.uuid.hex)

    user_by_session = await get_user_by_session(session=session, database_engine=engine, redis=redis)

    assert user_by_session is not None
    assert user_by_session.uuid == user.uuid


@pytest.mark.asyncio
async def test_if_session_expired(engine: AsyncEngine, redis: RedisInterface, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    await user.save(engine)
    session = "some_session"

    with pytest.raises(APIException) as exception_info:
        await get_user_by_session(session=session, database_engine=engine, redis=redis)
    assert exception_info.value.status == 403
    assert exception_info.value.errors == ["bad session"]


@pytest.mark.asyncio
async def test_if_user_deleted(engine: AsyncEngine, redis: RedisInterface, normal_users: list[UserDataClass]):
    user = User(
        name=normal_users[0].name,
        login=normal_users[0].login,
        password_hash=normal_users[0].password_hash,
    )
    await user.save(engine)
    session = "some_session"
    await redis.set(session, user.uuid.hex)
    await user.delete(engine)

    with pytest.raises(APIException) as exception_info:
        await get_user_by_session(session=session, database_engine=engine, redis=redis)
    assert exception_info.value.status == 403
    assert exception_info.value.errors == ["bad session"]


@pytest.mark.asyncio
async def test_if_session_is_none(engine: AsyncEngine, redis: RedisInterface):
    session = None
    with pytest.raises(APIException) as exception_info:
        await get_user_by_session(session=session, database_engine=engine, redis=redis)
    assert exception_info.value.status == 403
    assert exception_info.value.errors == ["bad session"]
