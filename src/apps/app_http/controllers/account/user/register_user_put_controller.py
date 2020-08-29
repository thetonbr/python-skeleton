from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response
from marshmallow import fields

from src.apps.app_http.controllers.controller import Controller
from src.libs.account.user.infrastructure.cqrs.register_user_command_handler import RegisterUserCommand


@final
class UserRegisterPutController(Controller):
    class RequestSchema(Controller.RequestSchema):
        id = fields.UUID(required=True, attribute='user_id')
        email = fields.Str(required=True)
        password = fields.Str(required=True)

    class ResponseSchema(Controller.ResponseSchema):
        id = fields.UUID(required=True)

    async def __call__(self, request: Request) -> Response:
        command = await self._validate(request, type_='users', type_class=RegisterUserCommand)
        await self._dispatch(command)
        return self._response(
            status_code=HTTPStatus.CREATED,
            data={
                'data': {
                    'id': command.user_id(),
                }
            },
            type_='users'
        )
