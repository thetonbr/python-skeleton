from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel

from project.libs.user.application.deleter_service import UserDeleterService
from project.libs.user.domain.properties import UserId


@final
class DeleteUserCommand(Command, BaseModel):
    user_id: str


@final
class DeleteUserCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserDeleterService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return DeleteUserCommand

    async def handle(self, command: DeleteUserCommand) -> None:
        await self._service(UserId(command.user_id))
