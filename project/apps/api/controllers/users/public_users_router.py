from http import HTTPStatus

from aioddd import CommandBus, QueryBus
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from project.apps.api.middleware.utils import get_current_dispatcher, get_current_asker
from project.libs.user.application.token_generator_service import TokenGeneratorResponse
from project.libs.user.infrastructure.cqrs.forget_user_password_command_handler import (
    ForgetUserPasswordCommand,
)
from project.libs.user.infrastructure.cqrs.generate_token_query_handler import (
    GenerateTokenQuery,
)
from project.libs.user.infrastructure.cqrs.register_user_command_handler import (
    RegisterUserCommand,
)
from project.libs.user.infrastructure.cqrs.reset_user_password_command_handler import (
    ResetUserPasswordCommand,
)

public_users = APIRouter()


@public_users.put(
    path='',
    status_code=HTTPStatus.CREATED,
    summary='Register User',
)
async def register_user_put_controller(
    command: RegisterUserCommand,
    dispatcher: CommandBus = Depends(get_current_dispatcher),
) -> None:
    await dispatcher.dispatch(command)


@public_users.post(
    path='/auth',
    response_model=TokenGeneratorResponse,
    status_code=HTTPStatus.OK,
    summary='Get JWT',
)
async def token_auth_post_controller(
    form: OAuth2PasswordRequestForm = Depends(),
    asker: QueryBus = Depends(get_current_asker),
) -> TokenGeneratorResponse:
    return await asker.ask(query=GenerateTokenQuery(email=form.username, password=form.password))


@public_users.post(
    path='/forget-password',
    status_code=HTTPStatus.OK,
    summary='Forget User password',
)
async def forget_user_password_post_controller(
    command: ForgetUserPasswordCommand,
    dispatcher: CommandBus = Depends(get_current_dispatcher),
) -> None:
    await dispatcher.dispatch(command)


@public_users.post(
    path='/reset-password',
    status_code=HTTPStatus.OK,
    summary='Reset User password',
)
async def reset_user_password_post_controller(
    command: ResetUserPasswordCommand,
    dispatcher: CommandBus = Depends(get_current_dispatcher),
) -> None:
    await dispatcher.dispatch(command)
