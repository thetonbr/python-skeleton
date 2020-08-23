import http
from typing import final

from aiohttp.web import Request, Response

from src.apps.cnf_http.controllers.controller import Controller


@final
class RootGetController(Controller):
    async def __call__(self, request: Request) -> Response:
        return self.response(
            status_code=http.HTTPStatus.OK,
            data={'type': 'service', 'id': 'service-configurator', 'attributes': None, 'meta': {}}
        )
