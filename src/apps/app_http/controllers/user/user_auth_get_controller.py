from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.read_user_auth_query_handler import ReadUserAuthQuery


@final
class UserAuthGetController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=False, attribute='user_id')
        token = fields.Str(required=True)

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)
        jwt = fields.Dict(required=True, keys=fields.Str(), values=fields.Raw())

    async def __call__(self, request: Request) -> Response:
        query = await self._validate({
            'data': {
                'type': 'users',
                'attributes': {
                    'token': request.headers.get('Authorization', ''),
                }
            }
        }, type_='users', type_class=ReadUserAuthQuery)
        res = await self._ask(query)
        return self._response(
            status_code=HTTPStatus.CREATED,
            data={
                'data': {
                    'id': res['user_id'],
                    'attributes': res['jwt']
                }
            },
            type_='users'
        )
