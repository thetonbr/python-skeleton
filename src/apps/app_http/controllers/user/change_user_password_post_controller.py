from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.change_user_password_command_handler import ChangeUserPasswordCommand


@final
class UserPasswordChangerPostController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=True, attribute='user_id')
        oldPassword = fields.Str(required=True, attribute='old_password')
        newPassword = fields.Str(required=True, attribute='new_password')

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)

    async def __call__(self, request: Request) -> Response:
        command = await self._validate(request, type_='users', type_class=ChangeUserPasswordCommand)
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
