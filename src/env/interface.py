from abc import ABC, abstractmethod


class EnvInterface(ABC):
    @property
    @abstractmethod
    def database_url(self) -> str: ...

    @property
    @abstractmethod
    def api_host(self) -> str: ...

    @property
    @abstractmethod
    def api_port(self) -> int: ...
