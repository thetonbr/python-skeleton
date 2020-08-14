from typing import final, Type

from aioddd import Command, CommandHandler

from src.libs.account.user.application.password_changer_service import UserPasswordChangerService
from src.libs.account.user.domain.properties import UserPassword
from src.libs.shared.domain.user.properties import UserId


@final
class ChangeUserPasswordCommand(Command):
    __slots__ = ('_user_id', '_old_password', '_new_password')

    def __init__(self, user_id: str, old_password: str, new_password: str) -> None:
        self._user_id = user_id
        self._old_password = old_password
        self._new_password = new_password

    def user_id(self) -> str:
        return self._user_id

    def old_password(self) -> str:
        return self._old_password

    def new_password(self) -> str:
        return self._new_password


@final
class ChangeUserPasswordCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserPasswordChangerService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return ChangeUserPasswordCommand

    async def handle(self, command: ChangeUserPasswordCommand) -> None:
        await self._service(UserId(command.user_id()), command.old_password(), UserPassword(command.new_password()))
