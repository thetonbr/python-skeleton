import http
from json import dumps
from logging import Logger
from traceback import TracebackException
from typing import Dict, final, Awaitable, Callable

from aioddd import BaseError, UnknownError, NotFoundError, ConflictError, BadRequestError, Id
from aiohttp.web import json_response, Request
from aiohttp.web_exceptions import HTTPNotFound, HTTPMethodNotAllowed
from aiohttp.web_response import StreamResponse
from marshmallow import ValidationError

from src.libs.account.user.domain.errors import UserUnauthorizedError


@final
class HttpErrorMiddleware:
    __slots__ = ('_logger', '_debug')

    def __init__(self, logger: Logger, debug: bool) -> None:
        self._logger = logger
        self._debug = debug

    async def __call__(
            self,
            request: Request,
            handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        try:
            return await handler(request)
        except Exception as err:
            if isinstance(err, (HTTPNotFound, HTTPMethodNotAllowed)):
                err = HttpRouteNotFoundError.create(detail={
                    'method': request.method.upper(),
                    'uri': request.url.path
                }).with_exception(err)
            base_error = self._map_to_base_error(err)
            status_code = self._map_status_code(err)
            errors = [
                {
                    'id': base_error.id(),
                    'links': {
                        'self': request.url.path
                    },
                    'status': str(status_code),
                    'code': base_error.code(),
                    'title': str(base_error.title()),
                    'detail': str(base_error.detail()),
                    'source': {
                        'pointer': '',
                    },
                    'meta': base_error.meta(),
                }
            ]
            if isinstance(err, ValidationError):
                _error = errors[0]
                _error['code'] = 'invalid_request_validation'
                errors = []
                for error in err.messages['errors']:
                    errors.append({
                        **_error,
                        'id': Id.generate().value(),
                        'title': error['detail'],
                        'detail': dumps({
                            'field': error['source']['pointer'].split('/')[-1],
                            'message': error['detail']
                        }),
                        'source': error['source'],
                        'meta': {
                            'errorCorrelationId': _error['id']
                        }
                    })
            data = {
                'errors': errors,
                'meta': {'traceback': self._exception_to_string(base_error)} if self._debug else {}
            }
            res = json_response(status=status_code, data=data)
            self._logger.info({'message': 'HTTP error', 'status': status_code, 'data': data})
            return res

    @staticmethod
    def _exception_to_string(err: BaseException) -> str:
        return ''.join(TracebackException.from_exception(err).format())

    @staticmethod
    def _map_to_base_error(err: Exception) -> BaseError:
        return err if isinstance(err, BaseError) else UnknownError.create().with_exception(err)

    @staticmethod
    def _errors_map() -> Dict[type, int]:
        return {
            UserUnauthorizedError: int(http.HTTPStatus.UNAUTHORIZED),
            NotFoundError: int(http.HTTPStatus.NOT_FOUND),
            ConflictError: int(http.HTTPStatus.CONFLICT),
            ValidationError: int(http.HTTPStatus.BAD_REQUEST),
            BadRequestError: int(http.HTTPStatus.BAD_REQUEST),
            HTTPNotFound: int(http.HTTPStatus.NOT_FOUND),
            UnknownError: int(http.HTTPStatus.INTERNAL_SERVER_ERROR),
        }

    @classmethod
    def _map_status_code(cls, err: Exception) -> int:
        for type_error, status_code in cls._errors_map().items():
            if isinstance(err, type_error):
                return status_code
        return int(http.HTTPStatus.INTERNAL_SERVER_ERROR)


@final
class HttpRouteNotFoundError(NotFoundError):
    _code = 'http_route_not_found'
    _title = 'Http route not found'
