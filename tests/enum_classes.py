from enum import Enum


class EnvVarEnumClass(Enum):
    DATABASE_URL: str = "sqlite+aiosqlite://"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_SESSION_TTL: int = 100
    API_SALT: str = "some_salt"
    REDIS_URL: str = "redis://127.0.0.1:6379"
