from typing import List, final

from aioddd import EventPublisher, Event, EventBus


@final
class InternalEventPublisher(EventPublisher):
    __slots__ = '_event_bus'

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    async def publish(self, events: List[Event]) -> None:
        await self._event_bus.notify(events=events)
