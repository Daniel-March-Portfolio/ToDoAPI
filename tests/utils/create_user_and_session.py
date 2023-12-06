from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import User
from src.core.redis import RedisInterface


async def create_user_and_session(
        login: str, name: str, password_hash: str, session: str, engine: AsyncEngine, redis: RedisInterface
) -> User:
    user = User(
        login=login,
        name=name,
        password_hash=password_hash
    )
    await user.save(engine)
    await redis.set(session, user.uuid.hex)
    return user
