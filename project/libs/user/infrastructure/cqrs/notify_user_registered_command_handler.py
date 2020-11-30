from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel

from project.libs.user.application.notifier_service import UserRegisteredNotifierService
from project.libs.user.domain.properties import UserEmail, UserId


@final
class NotifyUserRegisteredCommand(Command, BaseModel):
    id: str
    email: str


@final
class NotifyUserRegisteredCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserRegisteredNotifierService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return NotifyUserRegisteredCommand

    async def handle(self, command: NotifyUserRegisteredCommand) -> None:
        await self._service(UserId(command.id), UserEmail(command.email))
