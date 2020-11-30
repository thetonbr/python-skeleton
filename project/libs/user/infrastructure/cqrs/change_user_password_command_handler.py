from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel, Field

from project.libs.user.application.password_changer_service import (
    UserPasswordChangerService,
)
from project.libs.user.domain.properties import UserId, UserPassword


@final
class ChangeUserPasswordCommand(Command, BaseModel):
    user_id: str = Field(alias='id')
    old_password: str
    new_password: str


@final
class ChangeUserPasswordCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserPasswordChangerService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return ChangeUserPasswordCommand

    async def handle(self, command: ChangeUserPasswordCommand) -> None:
        await self._service(UserId(command.user_id), command.old_password, UserPassword(command.new_password))
