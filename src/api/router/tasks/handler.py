from src.api.router.tasks.methods import Delete, Get
from src.api.router.utils.base_view import BaseView


class Handler(BaseView):
    _get_method = Get
    _delete_method = Delete
