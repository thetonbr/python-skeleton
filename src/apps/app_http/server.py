from typing import Callable, Awaitable, Iterable

from aiohttp.web import Application as WebApplication, Request, StreamResponse

from src.libs.shared.infrastructure.container import Container

Guards = Iterable[Callable[[Request, Callable[[Request], Awaitable[StreamResponse]]], Awaitable[StreamResponse]]]


def build_server(container: Container) -> WebApplication:
    app = WebApplication(middlewares=[
        container.shared.http_app_error_middleware,
        # container.shared.http_app_logger_middleware.__call__
    ])
    middleware = [container.shared.http_app_auth_middleware.__call__]
    app.router.add_route(method='GET', path='/', handler=container.shared.http_app_root_get_controller.__call__)
    app.add_subapp(prefix='/public/users', subapp=_add_public_user_routes(container, middleware))
    app.add_subapp(prefix='/protected/users', subapp=_add_protected_user_routes(container, middleware))
    app.add_subapp(prefix='/private/users', subapp=_add_private_user_routes(container, middleware))
    return app


def _add_public_user_routes(container: Container, _: Guards) -> WebApplication:
    app = WebApplication()
    app.router.add_route(
        method='PUT',
        path='/register',
        handler=container.account.http_app_user_register_put_controller.__call__,
    )
    app.router.add_route(
        method='POST',
        path='/auth',
        handler=container.account.http_app_user_auth_post_controller.__call__,
    )
    return app


def _add_protected_user_routes(container: Container, _: Guards) -> WebApplication:
    app = WebApplication()
    app.router.add_route(
        method='GET',
        path='/auth',
        handler=container.account.http_app_user_auth_get_controller.__call__,
    )
    return app


def _add_private_user_routes(container: Container, middleware: Guards) -> WebApplication:
    app = WebApplication(middlewares=middleware)
    app.router.add_route(
        method='GET',
        path='/{user_id}',
        handler=container.account.http_app_user_finder_get_controller.__call__,
    )
    app.router.add_route(
        method='POST',
        path='/change-password',
        handler=container.account.http_app_user_password_changer_post_controller.__call__,
    )
    app.router.add_route(
        method='DELETE',
        path='/{user_id}',
        handler=container.account.http_app_user_deleter_delete_controller.__call__,
    )
    return app
