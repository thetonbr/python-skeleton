from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.delete_user_command_handler import DeleteUserCommand


@final
class UserDeleterDeleteController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=True, attribute='user_id')

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)

    async def __call__(self, request: Request) -> Response:
        command = await self._validate({
            'data': {
                'id': request.match_info.get('user_id'),
                'type': 'users',
            }
        }, type_='users', type_class=DeleteUserCommand)
        await self._auth_guard(request, command.user_id())
        await self._dispatch(command)
        return self._response(
            status_code=HTTPStatus.OK,
            data={
                'data': {
                    'id': command.user_id(),
                }
            },
            type_='users'
        )
