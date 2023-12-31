import pytest
from pytest_mock import MockerFixture

from src.core.exceptions import CoreException
from src.env import Env
from tests.enum_classes import EnvVarEnumClass


def test_env(mocker: MockerFixture):
    mocker.patch.dict(
        "os.environ",
        {
            EnvVarEnumClass.DATABASE_URL.name: EnvVarEnumClass.DATABASE_URL.value,
            EnvVarEnumClass.API_HOST.name: EnvVarEnumClass.API_HOST.value,
            EnvVarEnumClass.API_PORT.name: str(EnvVarEnumClass.API_PORT.value),
            EnvVarEnumClass.API_SESSION_TTL.name: str(EnvVarEnumClass.API_SESSION_TTL.value),
            EnvVarEnumClass.API_SALT.name: EnvVarEnumClass.API_SALT.value,
            EnvVarEnumClass.REDIS_URL.name: EnvVarEnumClass.REDIS_URL.value,
        }
    )
    env = Env()
    assert env.database_url == EnvVarEnumClass.DATABASE_URL.value
    assert env.api_host == EnvVarEnumClass.API_HOST.value
    assert env.api_port == EnvVarEnumClass.API_PORT.value
    assert env.api_session_ttl == EnvVarEnumClass.API_SESSION_TTL.value
    assert env.api_salt == EnvVarEnumClass.API_SALT.value
    assert env.redis_url == EnvVarEnumClass.REDIS_URL.value


def test_if_env_var_does_not_exists():
    with pytest.raises(CoreException) as exception_info:
        Env()
    expected_errors = {
        "DATABASE_URL not found in environment variables",
        "API_HOST not found in environment variables",
        "API_PORT not found in environment variables",
        "API_SESSION_TTL not found in environment variables",
        "API_SALT not found in environment variables",
        "REDIS_URL not found in environment variables",
    }
    assert set(exception_info.value.errors) == expected_errors


def test_if_env_var_has_wrong_type(mocker: MockerFixture):
    mocker.patch.dict(
        "os.environ",
        {
            EnvVarEnumClass.DATABASE_URL.name: EnvVarEnumClass.DATABASE_URL.value,
            EnvVarEnumClass.API_HOST.name: EnvVarEnumClass.API_HOST.value,
            EnvVarEnumClass.API_PORT.name: "not_integer",
            EnvVarEnumClass.API_SESSION_TTL.name: "not_integer",
            EnvVarEnumClass.API_SALT.name: EnvVarEnumClass.API_SALT.value,
            EnvVarEnumClass.REDIS_URL.name: EnvVarEnumClass.REDIS_URL.value,
        }
    )
    with pytest.raises(CoreException) as exception_info:
        Env()
    expected_errors = {
        "API_PORT is not an integer",
        "API_SESSION_TTL is not an integer",
    }
    assert set(exception_info.value.errors) == expected_errors
