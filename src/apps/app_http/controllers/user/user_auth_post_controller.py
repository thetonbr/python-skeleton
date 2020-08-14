from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.generate_token_query_handler import GenerateTokenQuery


@final
class UserAuthPostController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=False, attribute='user_id')
        email = fields.Str(required=True)
        password = fields.Str(required=True)

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)
        token = fields.Str(required=True)

    async def __call__(self, request: Request) -> Response:
        query = await self._validate(request, type_='users', type_class=GenerateTokenQuery)
        res = await self._ask(query)
        return self._response(
            status_code=HTTPStatus.OK,
            data={
                'data': {
                    'id': res['user_id'],
                    'attributes': {
                        'token': res['token']
                    }
                }
            },
            type_='users'
        )
