from logging import Logger
from time import time
from typing import final, Callable, Awaitable

from aiohttp.web import Request
from aiohttp.web_response import StreamResponse


@final
class HttpLoggerMiddleware:
    __slots__ = '_logger'

    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def __call__(
            self,
            request: Request,
            handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        correlation_id = id(request)
        start_time = time()
        self._logger.info({'message': 'HTTP request', 'data': {
            'method': request.method,
            'url': str(request.url),
            'start_time': start_time,
            'correlation_id': correlation_id
        }})
        response = await handler(request)
        self._logger.info({'message': 'HTTP response', 'data': {
            'method': request.method,
            'url': str(request.url),
            'status_code': int(response.status),
            'end_time': time(),
            'correlation_id': correlation_id
        }})
        return response
