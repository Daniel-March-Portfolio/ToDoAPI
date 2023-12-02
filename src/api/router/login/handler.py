from src.api.router.login.methods import Post
from src.api.router.utils.base_view import BaseView


class Handler(BaseView):
    _post_method = Post
