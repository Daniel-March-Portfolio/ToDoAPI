from core.exceptions._base_exception import CustomBaseException


class APIException(CustomBaseException):
    __status: int
    __errors: list[str]

    def __init__(self, status: int, errors: list[str]):
        self.__status = status
        self.__errors = errors

    @property
    def status(self) -> int:
        return self.__status

    @property
    def errors(self) -> list[str]:
        return self.__errors
