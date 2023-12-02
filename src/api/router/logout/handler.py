from src.api.router.logout.methods import Delete
from src.api.router.utils.base_view import BaseView


class Handler(BaseView):
    _delete_method = Delete
