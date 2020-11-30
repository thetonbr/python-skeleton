from typing import Type, final

from aioddd import Command, CommandHandler
from pydantic import BaseModel

from project.libs.user.application.password_resetter_service import (
    UserPasswordResetterService,
)
from project.libs.user.domain.properties import (
    UserEmail,
    UserPassword,
    UserRefreshToken,
)


@final
class ResetUserPasswordCommand(Command, BaseModel):
    email: str
    refresh_token: str
    new_password: str


@final
class ResetUserPasswordCommandHandler(CommandHandler):
    __slots__ = '_service'

    def __init__(self, service: UserPasswordResetterService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Command]:
        return ResetUserPasswordCommand

    async def handle(self, command: ResetUserPasswordCommand) -> None:
        await self._service(
            UserEmail(command.email), UserRefreshToken(command.refresh_token), UserPassword(command.new_password)
        )
