from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.find_user_query_handler import FindUserQuery


@final
class UserFinderGetController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=True, attribute='user_id')

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)
        email = fields.Str(required=True)

    async def __call__(self, request: Request) -> Response:
        query = await self._validate({
            'data': {
                'id': request.match_info.get('user_id'),
                'type': 'users',
            }
        }, type_='users', type_class=FindUserQuery)
        await self._auth_guard(request, query.user_id())
        return self._response(
            status_code=HTTPStatus.OK,
            data={
                'data': {
                    'id': query.user_id(),
                    'attributes': await self._ask(query)
                }
            },
            type_='users'
        )
