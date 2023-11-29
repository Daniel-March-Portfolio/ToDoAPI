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

    @property
    @abstractmethod
    def api_session_ttl(self) -> int:
        """Session TTL in seconds"""

    @property
    @abstractmethod
    def api_salt(self) -> str: ...
