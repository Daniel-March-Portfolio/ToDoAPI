from abc import ABC, abstractmethod

from src.api.state import State


class APIInterface(ABC):
    @property
    @abstractmethod
    def state(self) -> State: ...

    @abstractmethod
    def run(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
