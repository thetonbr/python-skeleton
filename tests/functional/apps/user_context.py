from json import loads

from behave import step  # pylint: disable=E0611
from behave.api.async_step import async_run_until_complete
from behave.runner import Context

from src.libs.account.user.infrastructure.cqrs.register_user_command_handler import RegisterUserCommand
from tests.functional import TEST_LOOP
from tests.unit.libs.account.user.domain.properties_mothers import UserIdMother, UserEmailMother, UserPasswordMother


class UserContext:
    @staticmethod
    @step('an existent user with id "{user_id}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_user_with_id(ctx: Context, user_id: str) -> None:
        user_id = UserIdMother.create(user_id).value()
        await ctx.container.command_bus.dispatch(RegisterUserCommand(
            user_id,
            UserEmailMother.random().value(),
            'secret123456'
        ))

    @staticmethod
    @step('an existent user with')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_user_with(ctx: Context) -> None:
        cmd = loads(ctx.text)
        user_id = (UserIdMother.create(cmd['id']) if 'id' in cmd else UserIdMother.random()).value()
        plain_password = cmd['password'] if 'password' in cmd else 'secret123456'
        UserPasswordMother.create(plain_password, hashed=False).check(plain_password)
        await ctx.container.command_bus.dispatch(RegisterUserCommand(
            user_id,
            (UserEmailMother.create(cmd['email']) if 'email' in cmd else UserEmailMother.random()).value(),
            plain_password
        ))

    @staticmethod
    @step('an authenticated user with email "{email}" and password "{password}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_authenticated_user_with_email_and_password(ctx: Context, email: str, password: str) -> None:
        ctx.token = (await ctx.container.token_generator_service(UserEmailMother.create(email), password))['token']

    @staticmethod
    @step('an existent authenticated user with id "{user_id}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_authenticated_user_with_id(ctx: Context, user_id: str) -> None:
        cmd = {'id': user_id}
        email = UserEmailMother.create(cmd['email']) if 'email' in cmd else UserEmailMother.random()
        plain_password = cmd['password'] if 'password' in cmd else 'secret123456'
        await ctx.container.command_bus.dispatch(RegisterUserCommand(
            user_id,
            email.value(),
            plain_password
        ))
        ctx.token = (await ctx.container.token_generator_service(email, plain_password))['token']

    @staticmethod
    @step('an existent authenticated user with')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_authenticated_user_with(ctx: Context) -> None:
        cmd = loads(ctx.text)
        email = UserEmailMother.create(cmd['email']) if 'email' in cmd else UserEmailMother.random()
        plain_password = cmd['password'] if 'password' in cmd else 'secret123456'
        UserPasswordMother.create(plain_password, hashed=False).check(plain_password)
        await ctx.container.command_bus.dispatch(RegisterUserCommand(
            (UserIdMother.create(cmd['id']) if 'id' in cmd else UserIdMother.random()).value(),
            email.value(),
            plain_password
        ))
        ctx.token = (await ctx.container.token_generator_service(email, plain_password))['token']
