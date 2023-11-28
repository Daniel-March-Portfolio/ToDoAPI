import typing
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models._base import BaseModel

if typing.TYPE_CHECKING:
    from src.core.models.task import Task


class User(BaseModel):
    __tablename__ = "user"

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    login: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    tasks: Mapped[List["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
