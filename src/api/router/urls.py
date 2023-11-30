from dataclasses import dataclass


@dataclass(frozen=True)
class URLs:
    task = "/task"
    tasks = "/tasks"
    login = "/login"
    logout = "/logout"
    register = "/register"
