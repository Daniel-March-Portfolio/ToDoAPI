from enum import Enum
from typing import Any

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Mapped

from src.constants import EMPTY


class OPERATOR(Enum):
    IN = "in"
    NOT_IN = "not_in"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    MORE = "more"
    MORE_OR_EQUAL = "more_or_equal"
    LESS = "less"
    LESS_OR_EQUAL = "less_or_equal"


def create_condition(model_field: Mapped, value: Any, operator: OPERATOR = None) -> BinaryExpression | None:
    if value is EMPTY:
        return None
    if operator is None:
        operator = OPERATOR.IN if isinstance(value, (list, tuple)) else OPERATOR.EQUAL
    match operator:
        case OPERATOR.IN:
            return model_field.in_(value)
        case OPERATOR.NOT_IN:
            return model_field.not_in(value)
        case OPERATOR.EQUAL:
            return model_field == value
        case OPERATOR.NOT_EQUAL:
            return model_field != value
        case OPERATOR.MORE:
            return model_field > value
        case OPERATOR.MORE_OR_EQUAL:
            return model_field >= value
        case OPERATOR.LESS:
            return model_field < value
        case OPERATOR.LESS_OR_EQUAL:
            return model_field <= value
