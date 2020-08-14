from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller


@final
class RootGetController(Controller):
    class ResponseSchema(Controller.ResponseSchema):
        id = fields.Str(required=True)

    async def __call__(self, request: Request) -> Response:
        return self._response(
            status_code=HTTPStatus.OK,
            data={
                'data': {
                    'id': 'example'
                }
            },
            type_='service'
        )
