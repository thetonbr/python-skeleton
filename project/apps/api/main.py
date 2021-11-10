from typing import Any, Callable, Type, Union

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from project.apps.api.controllers import (
    private_users,
    protected_users,
    public_global,
    public_users,
)
from project.apps.api.middleware.exception_handler import APIErrors, exception_handler
from project.apps.settings import container, env

debug = env(key='debug', typ=bool)

app = FastAPI(
    debug=debug,
    default_response_class=ORJSONResponse,  # better performance
    openapi_url=env(key="openapi_url", typ=str),
    openapi_prefix=env(key="openapi_prefix", typ=str),
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    title=env(key='name', typ=str),
    version=env(key='version', typ=str),
    on_startup=[container],  # to avoid event_loop issues with third parties
    on_shutdown=[lambda: container().get('services.shutdown')()],
)


def _add_exception_handler(exc_classes: list[Union[int, Type[Exception]]], handlers: list[Callable]) -> None:
    for exc_class_or_status_code in exc_classes:
        for handler in handlers:
            app.add_exception_handler(exc_class_or_status_code=exc_class_or_status_code, handler=handler)


def _add_middleware(middleware_classes: list[type], **options: Any) -> None:
    for middleware_class in middleware_classes:
        app.add_middleware(middleware_class=middleware_class, **options)


def _include_router(router: APIRouter, prefix: str, tags: list[str]) -> None:
    app.include_router(
        router=router,
        prefix=prefix,
        tags=tags,
        responses={
            400: {'model': APIErrors},
            401: {'model': APIErrors},
            403: {'model': APIErrors},
            404: {'model': APIErrors},
            409: {'model': APIErrors},
            422: {'model': APIErrors},
            500: {'model': APIErrors},
        },
    )  # to avoid hardcoded ValidationError BaseModel


_add_exception_handler([500, Exception, HTTPException, RequestValidationError], [exception_handler])

_add_middleware([CORSMiddleware], allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_include_router(public_global, '', [])
_include_router(public_users, '/api/public/users', ['users'])
_include_router(protected_users, '/api/protected/users', ['users'])
_include_router(private_users, '/api/private/users', ['users'])


def main() -> None:
    from uvicorn import run  # pylint: disable=C0415

    run(
        app='main:app',
        host=env(key='http_host', typ=str),
        port=env(key='http_port', typ=int),
        log_level=env(key='log_level', typ=str).lower(),  # type: ignore
        reload=debug,
    )  # pragma: no cover
