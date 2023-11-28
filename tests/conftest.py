import asyncio

from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.database import create_engine
from src.core.database.engine import drop_all_tables, create_all_tables


@fixture(autouse=True, scope="function")
def engine() -> AsyncEngine:
    engine = create_engine(url="sqlite+aiosqlite://", echo=False)
    asyncio.run(drop_all_tables(engine=engine))
    asyncio.run(create_all_tables(engine=engine))
    return engine
