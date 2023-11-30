from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from core.exceptions import APIException
from core.models import User
from core.redis import RedisInterface
from core.utils.create_condition import create_condition


async def get_user_by_session(database_engine: AsyncEngine, session: str | None, redis: RedisInterface) -> User:
    if session is None:
        raise APIException(status=403, errors=["bad session"])

    bytes_user_uuid_by_session_in_redis: bytes | None = await redis.get(session)
    if bytes_user_uuid_by_session_in_redis is None:
        raise APIException(status=403, errors=["bad session"])

    user_uuid_by_session_in_redis = UUID(bytes_user_uuid_by_session_in_redis.decode())
    user = await User.filter(
        create_condition(User.uuid, user_uuid_by_session_in_redis),
        engine=database_engine,
        fetch_one=True

    )
    if user is None:
        raise APIException(status=403, errors=["bad session"])

    return user
