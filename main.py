import asyncio
import logging

from src.api import API
from src.core.database import create_engine, create_all_tables
from src.core.redis import Redis
from src.env import Env

logging.basicConfig(level=logging.DEBUG)


async def main():
    environment = Env()
    redis = Redis(url=f"redis://{environment.redis_host}:{environment.redis_port}")
    engine = create_engine(environment.database_url)
    await create_all_tables(engine)

    api = API(
        env=environment,
        database_engine=engine,
        redis=redis
    )
    await api.run()


asyncio.run(main())
