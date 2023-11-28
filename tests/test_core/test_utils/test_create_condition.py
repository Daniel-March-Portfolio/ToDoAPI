from typing import Any

import pytest

from src.constants import EMPTY
from src.core.utils.create_condition import OPERATOR, create_condition


class EchoOperator:
    def __lt__(self, other):
        return "__lt__"

    def __le__(self, other):
        return "__le__"

    def __eq__(self, other):
        return "__eq__"

    def __ne__(self, other):
        return "__ne__"

    def __gt__(self, other):
        return "__gt__"

    def __ge__(self, other):
        return "__ge__"

    def in_(self, *args, **kwargs):
        return "in_"

    def not_in(self, *args, **kwargs):
        return "not_in"


@pytest.mark.parametrize(
    "value,operator,response",
    [
        [EMPTY, None, None],
        [[], None, "in_"],
        [None, None, "__eq__"],
        ["some_value", None, "__eq__"],
        ["some_value", OPERATOR.MORE, "__gt__"],
        ["some_value", OPERATOR.IN, "in_"],
        ["some_value", OPERATOR.NOT_IN, "not_in"],
        ["some_value", OPERATOR.EQUAL, "__eq__"],
        ["some_value", OPERATOR.NOT_EQUAL, "__ne__"],
        ["some_value", OPERATOR.MORE_OR_EQUAL, "__ge__"],
        ["some_value", OPERATOR.LESS, "__lt__"],
        ["some_value", OPERATOR.LESS_OR_EQUAL, "__le__"],
    ]
)
def test_create_condition(value: Any, operator: OPERATOR, response: str):
    echo_operator = EchoOperator()
    assert create_condition(echo_operator, value, operator) == response
