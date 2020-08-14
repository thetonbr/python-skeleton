from json import dumps
from logging import Logger
from typing import final, Callable, Awaitable

from aiohttp.web import Request
from aiohttp.web_response import StreamResponse

from src.libs.account.user.application.authenticator_service import AuthenticatorService


@final
class HttpAuthMiddleware:
    __slots__ = ('_logger', '_service')

    def __init__(self, logger: Logger, service: AuthenticatorService) -> None:
        self._logger = logger
        self._service = service

    async def __call__(
            self,
            request: Request,
            handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        if 'Authorization' not in request.headers:
            raise Exception('Authorization header key required!')
        request.setdefault('user_auth', dumps(await self._service(request.headers['Authorization'])))
        return await handler(request)
