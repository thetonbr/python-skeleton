from typing import Any, Dict, Optional, final

from aioddd import CommandBus, QueryBus

from project.apps.settings import container
from project.libs.user.application.finder_service import UserFullFinderResponse
from project.libs.user.application.token_generator_service import TokenGeneratorService
from project.libs.user.infrastructure.cqrs.find_user_query_handler import (
    FindFullUserQuery,
)
from project.libs.user.infrastructure.cqrs.forget_user_password_command_handler import (
    ForgetUserPasswordCommand,
)
from project.libs.user.infrastructure.cqrs.register_user_command_handler import (
    RegisterUserCommand,
)
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
)


@final
class UserContext:
    @classmethod
    async def an_existent_user_with_id(cls, user_id: str) -> str:
        return str(await cls._register_user(cmd={'id': user_id}, do_authorize=True))

    @classmethod
    async def an_existent_user_with(cls, cmd: Dict[str, Any]) -> None:
        _ = await cls._register_user(cmd=cmd, do_authorize=False)

    @classmethod
    async def an_authenticated_user_with_email_and_password(cls, email: str, password: str) -> str:
        return await cls._authorize_user({'email': email, 'password': password})

    @classmethod
    async def find_full_user_with_id(cls, user_id: str) -> UserFullFinderResponse:
        return await cls._find_full_user(user_id)

    @classmethod
    async def forget_user_password_with_email(cls, email: str) -> None:
        await cls._forget_user_password({'email': email})

    @classmethod
    async def an_existent_authenticated_user_with_id(cls, user_id: str) -> str:
        return str(await cls._register_user(cmd={'id': user_id}, do_authorize=True))

    @classmethod
    async def an_existent_authenticated_user_with(cls, cmd: Dict[str, Any]) -> str:
        return str(await cls._register_user(cmd=cmd, do_authorize=True))

    @staticmethod
    async def _find_full_user(user_id: str) -> UserFullFinderResponse:
        return (
            await container()
            .get(QueryBus)
            .ask(
                FindFullUserQuery(
                    **{
                        'user_id': (UserIdMother.create(user_id)).value(),
                    }
                )
            )
        )

    @staticmethod
    async def _authorize_user(cmd: Dict[str, Any]) -> str:
        res = await container().get(TokenGeneratorService)(
            **{
                'email': UserEmailMother.create(cmd['email']),
                'password': cmd['password'],
            }
        )
        return f'{res.token_type} {res.access_token}'

    @classmethod
    async def _register_user(cls, cmd: Dict[str, Any], do_authorize: bool) -> Optional[str]:
        plain_email = (UserEmailMother.create(cmd['email']) if 'email' in cmd else UserEmailMother.random()).value()
        plain_password = cmd['password'] if 'password' in cmd else UserPasswordMother.random().value()
        await container().get(CommandBus).dispatch(
            RegisterUserCommand(
                **{
                    'id': (UserIdMother.create(cmd['id']) if 'id' in cmd else UserIdMother.random()).value(),
                    'email': plain_email,
                    'password': plain_password,
                }
            )
        )
        if do_authorize:
            return await cls._authorize_user(cmd={'email': plain_email, 'password': plain_password})
        return None

    @staticmethod
    async def _forget_user_password(cmd: Dict[str, Any]) -> None:
        await container().get(CommandBus).dispatch(
            ForgetUserPasswordCommand(
                **{
                    'email': UserEmailMother.create(cmd['email']).value(),
                }
            )
        )
