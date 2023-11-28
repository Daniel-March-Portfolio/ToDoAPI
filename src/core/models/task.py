import typing
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models._base import BaseModel

if typing.TYPE_CHECKING:
    from src.core.models.user import User


class Task(BaseModel):
    __tablename__ = "task"

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="tasks")
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("user.uuid"))
