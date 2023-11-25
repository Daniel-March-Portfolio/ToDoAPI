from typing import Sequence, Self

from sqlalchemy import select, func, BinaryExpression, and_
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped


class BaseModel(DeclarativeBase):
    @classmethod
    async def get_count_of_rows(cls, engine: AsyncEngine) -> int:
        async with AsyncSession(engine) as session:
            return await session.scalar(select(func.count()).select_from(cls))

    @classmethod
    async def get_all(
            cls, engine: AsyncEngine, offset: int = None, limit: int = None, order_by: list[Mapped] = None
    ) -> Sequence[Self]:
        async with AsyncSession(engine) as session:
            rows = await session.scalars(select(cls).order_by(*order_by or []).offset(offset).limit(limit))
            return rows.fetchall()

    @classmethod
    async def filter(
            cls, *conditions: BinaryExpression, limit: int = None, offset: int = None, order_by: tuple[Mapped] = None,
            engine: AsyncEngine, fetch_one: bool = False
    ) -> Sequence[Self] | Self | None:
        order_by = order_by or ()
        stmt = (select(cls)
                .where(and_(*conditions))
                .limit(limit)
                .offset(offset)
                .order_by(*order_by))
        async with AsyncSession(engine) as session:
            if fetch_one:
                result = await session.scalar(stmt)
            else:
                records = await session.scalars(stmt)
                result = records.fetchall()
        return result

    async def save(self, engine: AsyncEngine) -> Self:
        async with AsyncSession(engine) as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)
        return self

    async def delete(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            await session.delete(self)
            await session.commit()
