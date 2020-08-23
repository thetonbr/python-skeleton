from typing import Callable, Awaitable, Iterable

from aiohttp.web import Application as WebApplication, Request, StreamResponse

from src.libs.shared.infrastructure.configurator.container import Container

Guards = Iterable[Callable[[Request, Callable[[Request], Awaitable[StreamResponse]]], Awaitable[StreamResponse]]]


def build_server(container: Container) -> WebApplication:
    app = WebApplication()
    app.router.add_route(method='GET', path='/', handler=container.http_app_root_get_controller.__call__)
    app.add_subapp(prefix='/api/cnf/protected', subapp=_add_protected_routes(container))
    return app


def _add_protected_routes(container: Container) -> WebApplication:
    app = WebApplication()
    app.router.add_route(
        method='GET',
        path='/amqp-setup',
        handler=container.http_app_setup_amqp_get_controller.__call__,
    )
    app.router.add_route(
        method='GET',
        path='/amqp-clean',
        handler=container.http_app_clean_amqp_get_controller.__call__,
    )
    app.router.add_route(
        method='GET',
        path='/mongodb-setup',
        handler=container.http_app_setup_mongodb_get_controller.__call__,
    )
    app.router.add_route(
        method='GET',
        path='/mongodb-clean',
        handler=container.http_app_clean_mongodb_get_controller.__call__,
    )
    return app
