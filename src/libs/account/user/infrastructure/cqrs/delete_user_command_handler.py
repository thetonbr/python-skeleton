from typing import final, Type

from aioddd import Command, CommandHandler

from src.libs.account.user.application.deleter_service import UserDeleterService
from src.libs.shared.domain.user.properties import UserId


@final
class DeleteUserCommand(Command):
    __slots__ = '_user_id'

    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    def user_id(self) -> str:
        return self._user_id


@final
class DeleteUserCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserDeleterService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return DeleteUserCommand

    async def handle(self, command: DeleteUserCommand) -> None:
        await self._service(UserId(command.user_id()))
