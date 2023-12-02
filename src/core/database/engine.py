from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from src.core.models import BaseModel


def create_engine(url: str, echo: bool = False) -> AsyncEngine:
    engine = create_async_engine(url, echo=echo)
    return engine


async def create_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def drop_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
