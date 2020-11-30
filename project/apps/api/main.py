from os.path import realpath
from typing import Callable, List, Type

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from uvicorn import run

from project.apps.api.controllers import (
    private_users,
    protected_users,
    public_global,
    public_users,
)
from project.apps.api.middleware.exception_handler import APIErrors, exception_handler
from project.apps.settings import container, env

debug = env(key='environment', typ=str) != 'production'

app = FastAPI(
    debug=debug,
    default_response_class=ORJSONResponse,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    title=env(key='name', typ=str),
    version=env(key='version', typ=str),
    on_startup=[container],  # to avoid event_loop issues with third parties
    on_shutdown=[lambda: container().get('services.shutdown')()],
)


def _add_exception_handler(exc_class: Type[Exception], handler: Callable) -> None:
    app.add_exception_handler(exc_class_or_status_code=exc_class, handler=handler)


def _include_router(router: APIRouter, prefix: str, tags: List[str]) -> None:
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
    )  # to avoid hardcoded ValidationError


if debug:
    app.mount('/static', StaticFiles(directory=realpath(f'{realpath(__file__)}/../../../static')), name='static')

_add_exception_handler(HTTPException, exception_handler)
_add_exception_handler(RequestValidationError, exception_handler)
_add_exception_handler(Exception, exception_handler)

_include_router(public_global, '', [])
_include_router(public_users, '/api/public/users', ['users'])
_include_router(protected_users, '/api/protected/users', ['users'])
_include_router(private_users, '/api/private/users', ['users'])


def main() -> None:
    run(
        app='main:app',
        host=env(key='http_host', typ=str),
        port=env(key='http_port', typ=int),
        log_level=env(key='log_level', typ=str).lower(),  # type: ignore
        reload=debug,
    )  # pragma: no cover
