from typing import final, Type

from aioddd import Command, CommandHandler

from src.libs.account.user.application.register_service import UserRegisterService
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.shared.domain.user.properties import UserId


@final
class RegisterUserCommand(Command):
    __slots__ = ('_user_id', '_email', '_password')

    def __init__(self, user_id: str, email: str, password: str) -> None:
        self._user_id = user_id
        self._email = email
        self._password = password

    def user_id(self) -> str:
        return self._user_id

    def email(self) -> str:
        return self._email

    def password(self) -> str:
        return self._password


@final
class RegisterUserCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserRegisterService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return RegisterUserCommand

    async def handle(self, command: RegisterUserCommand) -> None:
        await self._service(UserId(command.user_id()), UserEmail(command.email()), UserPassword(command.password()))
