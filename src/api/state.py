from enum import Enum


class State(Enum):
    INITIALIZED = "initialized"
    STOPPED = "stopped"
    RUNNING = "running"
    STOPPING = "stopping"
