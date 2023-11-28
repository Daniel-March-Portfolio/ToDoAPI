import pytest

from src.core.utils.hash_password import hash_password


@pytest.mark.parametrize(
    "first_params,second_params",
    [
        [("password1", "login", "salt"), ("password2", "login", "salt")],
        [("password", "login1", "salt"), ("password", "login2", "salt")],
        [("password", "login", "salt1"), ("password", "login", "salt2")],
    ]
)
def test_hash_password(first_params: tuple[str, str, str], second_params: tuple[str, str, str]):
    assert hash_password(*first_params) == hash_password(*first_params)
    assert hash_password(*second_params) == hash_password(*second_params)
    assert hash_password(*first_params) != hash_password(*second_params)
