from src.api.router.task.methods import Get, Post, Put, Delete
from src.api.router.utils.base_view import BaseView


class Handler(BaseView):
    _get_method = Get
    _post_method = Post
    _put_method = Put
    _delete_method = Delete
