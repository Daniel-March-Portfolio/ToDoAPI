import json
from dataclasses import dataclass
from typing import Any

from src.api import APIInterface


@dataclass
class RequestDataClass:
    api: APIInterface
    raw_json: dict | Any

    async def json(self) -> dict:
        if isinstance(self.raw_json, dict):
            return self.raw_json
        return json.loads(self.raw_json)
