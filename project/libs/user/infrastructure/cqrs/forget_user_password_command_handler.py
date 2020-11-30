from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel

from project.libs.user.application.password_forget_service import (
    UserPasswordForgetService,
)
from project.libs.user.domain.properties import UserEmail


@final
class ForgetUserPasswordCommand(Command, BaseModel):
    email: str


@final
class ForgetUserPasswordCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserPasswordForgetService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return ForgetUserPasswordCommand

    async def handle(self, command: ForgetUserPasswordCommand) -> None:
        await self._service(UserEmail(command.email))
