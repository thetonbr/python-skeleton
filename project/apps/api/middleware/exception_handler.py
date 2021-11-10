from http import HTTPStatus
from traceback import TracebackException
from typing import Any, cast, final

from aioddd import (
    BadRequestError,
    BaseError,
    ConflictError,
    Id,
    NotFoundError,
    UnauthorizedError,
    UnknownError,
)
from fastapi import Depends, Request
from fastapi.responses import ORJSONResponse
from orjson import dumps, loads
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException

from project.apps.api.middleware.utils import is_debug


@final
class APIError(BaseModel):
    id: str
    links: dict[str, str]
    status: str
    code: str
    title: str
    detail: str
    source: dict[str, str]
    meta: dict[str, Any]


@final
class APIErrors(BaseModel):
    errors: list[APIError]
    meta: dict[str, Any]


def exception_handler(req: Request, err: BaseException, debug: bool = Depends(is_debug)) -> ORJSONResponse:
    base_error = _map_to_base_error(req=req, err=err)
    status_code = _map_status_code(err=base_error)
    errors = [_err_to_dict(err=base_error, status_code=str(status_code), self=req.url.path)]
    if isinstance(err, ValidationError):
        errors = _add_validations_errors(err=cast(ValidationError, err), errors=errors)
    return ORJSONResponse(
        status_code=status_code,
        content=APIErrors(
            errors=errors,
            meta={'traceback': _exception_to_string(base_error)} if debug else {},
        ).dict(),
    )


def _exception_to_string(err: BaseException) -> str:
    return ''.join(TracebackException.from_exception(err).format())


def _map_to_base_error(req: Request, err: BaseException) -> BaseError:
    if isinstance(err, BaseError):
        return cast(BaseError, err)
    if isinstance(err, HTTPException):
        matches = {400: BadRequestError, 401: UnauthorizedError, 404: NotFoundError, 409: ConflictError}
        http_err = cast(HTTPException, err)
        if len(err.args) == 0:
            err.args = (http_err.detail,)
        if err_class := matches.get(http_err.status_code, None):
            return err_class.create(detail={'route': req.url.path}).with_exception(http_err)
    if isinstance(err, ValidationError):
        val_err = cast(ValidationError, err)
        return BadRequestError.create(detail=loads(val_err.json())).with_exception(val_err)
    return UnknownError.create().with_exception(err)


def _errors_map() -> dict[type, int]:
    return {
        UnauthorizedError: int(HTTPStatus.UNAUTHORIZED),
        NotFoundError: int(HTTPStatus.NOT_FOUND),
        ConflictError: int(HTTPStatus.CONFLICT),
        BadRequestError: int(HTTPStatus.BAD_REQUEST),
        UnknownError: int(HTTPStatus.INTERNAL_SERVER_ERROR),
    }


def _map_status_code(err: BaseException) -> int:
    for type_error, status_code in _errors_map().items():
        if isinstance(err, type_error):
            return status_code
    return int(HTTPStatus.INTERNAL_SERVER_ERROR)


def _err_to_dict(err: BaseError, status_code: str, self: str) -> APIError:
    return APIError(
        id=err.id(),
        links={'self': self},
        status=status_code,
        code=err.code()[0] if isinstance(err.code(), tuple) else err.code(),
        title=err.title()[0] if isinstance(err.title(), tuple) else err.title(),
        detail=str(err.detail()),
        source={'pointer': ''},
        meta=err.meta(),
    )


def _add_validations_errors(err: ValidationError, errors: list[APIError]) -> list[APIError]:
    _error = errors[0]
    _error.code = 'invalid_request_validation'
    errors = []
    for error in err.errors():
        errors.append(
            APIError(
                **{
                    **_error.dict(),
                    'id': Id.generate().value(),
                    'title': error['msg'],
                    'detail': dumps(
                        {
                            'field': list(error['loc'])[1:],
                            'message': f'{error["msg"]}: {error["type"]}',
                        }
                    ).decode('utf-8'),
                    'source': {'pointer': error['loc'][0]},
                    'meta': {'error_correlation_id': _error.id},
                }
            )
        )
    return errors
