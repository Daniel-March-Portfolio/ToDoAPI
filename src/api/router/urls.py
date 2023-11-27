from dataclasses import dataclass


@dataclass
class URLs:
    user = "/user"
    task = "/task"
    tasks = "/tasks"
    login = "/login"
    logout = "/logout"
    register = "/register"
