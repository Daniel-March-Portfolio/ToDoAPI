from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDataClass:
    uuid: UUID
    name: str
    login: str
    password: str
    password_hash: str
    created_at: datetime


@dataclass
class TaskDataClass:
    uuid: UUID
    title: str
    created_at: datetime
