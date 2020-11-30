from typing import List, Type, final

from aioddd import CommandBus, Event, EventHandler

from project.libs.user.domain.errors import UserNotFoundError
from project.libs.user.domain.events import UserRegistered
from project.libs.user.infrastructure.cqrs.notify_user_registered_command_handler import (
    NotifyUserRegisteredCommand,
)


@final
class NotifyUserRegisteredOnUserRegisteredEventHandler(EventHandler):
    __slots__ = '_command_bus'

    def __init__(self, command_bus: CommandBus) -> None:
        self._command_bus = command_bus

    def subscribed_to(self) -> List[Type[Event]]:
        return [UserRegistered]

    async def handle(self, events: List[Event]) -> None:
        for event in events:
            if isinstance(event, UserRegistered):
                await self._handle(event)

    async def _handle(self, event: UserRegistered) -> None:
        try:
            await self._command_bus.dispatch(
                NotifyUserRegisteredCommand(id=event.attributes.id.value(), email=event.attributes.email.value())
            )
        except UserNotFoundError:
            pass
