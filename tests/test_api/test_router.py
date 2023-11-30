from aiohttp.web_routedef import view

from src.api.router import Router

AMOUNT_OF_USED_URLS = 5


def test_paths_for_routes():
    router = Router()
    used_paths = set()

    assert len(router.routes) == AMOUNT_OF_USED_URLS

    for route in router.routes:
        assert route.path not in used_paths
        used_paths.add(route.path)


def test_add_route():
    router = Router()
    new_path = "/new_path"

    used_paths = set()
    for route in router.routes:
        used_paths.add(route.path)
    assert new_path not in used_paths

    router.add_route(view(new_path, None))

    used_paths = set()
    for route in router.routes:
        used_paths.add(route.path)
    assert new_path in used_paths
