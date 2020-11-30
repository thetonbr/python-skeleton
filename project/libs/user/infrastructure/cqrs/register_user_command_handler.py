from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel, Field

from project.libs.user.application.register_service import UserRegisterService
from project.libs.user.domain.properties import UserEmail, UserId, UserPassword


@final
class RegisterUserCommand(Command, BaseModel):
    user_id: str = Field(alias='id')
    email: str
    password: str


@final
class RegisterUserCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserRegisterService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return RegisterUserCommand

    async def handle(self, command: RegisterUserCommand) -> None:
        await self._service(UserId(command.user_id), UserEmail(command.email), UserPassword(command.password))
