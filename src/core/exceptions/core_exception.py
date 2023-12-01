from src.core.exceptions._base_exception import CustomBaseException


class CoreException(CustomBaseException):
    __errors: list[str]

    def __init__(self, errors: list[str]):
        self.__errors = errors

    @property
    def errors(self) -> list[str]:
        return self.__errors
