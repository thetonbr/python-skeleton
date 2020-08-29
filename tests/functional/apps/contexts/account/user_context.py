from json import loads
from typing import Dict, Any

from behave import step  # pylint: disable=E0611
from behave.api.async_step import async_run_until_complete
from behave.runner import Context

from src.libs.account.user.infrastructure.cqrs.register_user_command_handler import RegisterUserCommand
from tests.functional import TEST_LOOP
from tests.unit.libs.account.user.domain.properties_mothers import UserIdMother, UserEmailMother, UserPasswordMother

DEFAULT_PASSWORD = 'secret123456'


async def _authorize_user(ctx: Context, cmd: Dict[str, Any]) -> None:
    res = await ctx.container.account.token_generator_service(UserEmailMother.create(cmd['email']), cmd['password'])
    ctx.token = res['token']


async def _register_user(ctx: Context, cmd: Dict[str, Any], do_authorize: bool) -> None:
    user_id = (UserIdMother.create(cmd['id']) if 'id' in cmd else UserIdMother.random()).value()
    plain_email = (UserEmailMother.create(cmd['email']) if 'email' in cmd else UserEmailMother.random()).value()
    plain_password = cmd['password'] if 'password' in cmd else DEFAULT_PASSWORD
    UserPasswordMother.create(plain_password, hashed=False).check(plain_password)
    await ctx.container.shared.command_bus.dispatch(RegisterUserCommand(user_id, plain_email, plain_password))
    if do_authorize:
        await _authorize_user(ctx=ctx, cmd={'email': plain_email, 'password': plain_password})


class UserContext:
    @staticmethod
    @step('an existent user with id "{user_id}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_user_with_id(ctx: Context, user_id: str) -> None:
        await _register_user(ctx=ctx, cmd={'id': user_id}, do_authorize=True)

    @staticmethod
    @step('an existent user with')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_user_with(ctx: Context) -> None:
        await _register_user(ctx=ctx, cmd=loads(ctx.text), do_authorize=False)

    @staticmethod
    @step('an authenticated user with email "{email}" and password "{password}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_authenticated_user_with_email_and_password(ctx: Context, email: str, password: str) -> None:
        await _authorize_user(ctx, {'email': email, 'password': password})

    @staticmethod
    @step('an existent authenticated user with id "{user_id}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_authenticated_user_with_id(ctx: Context, user_id: str) -> None:
        await _register_user(ctx=ctx, cmd={'id': user_id}, do_authorize=True)

    @staticmethod
    @step('an existent authenticated user with')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_authenticated_user_with(ctx: Context) -> None:
        await _register_user(ctx=ctx, cmd=loads(ctx.text), do_authorize=True)
