from dataclasses import dataclass


@dataclass(frozen=True)
class URLs:
    user = "/user"
    task = "/task"
    tasks = "/tasks"
    login = "/login"
    logout = "/logout"
    register = "/register"
