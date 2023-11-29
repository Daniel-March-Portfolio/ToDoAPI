import json
from dataclasses import dataclass, field
from typing import Any

from src.api import APIInterface


@dataclass
class RequestDataClass:
    api: APIInterface
    raw_json: dict | Any = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)

    async def json(self) -> dict:
        if isinstance(self.raw_json, dict):
            return self.raw_json
        return json.loads(self.raw_json)
