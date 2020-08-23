from typing import List, final

from aioddd import EventPublisher, Event


@final
class EventPublisherDecorator(EventPublisher):
    _publishers: List[EventPublisher]

    def __init__(self, publishers: List[EventPublisher]) -> None:
        self._publishers = publishers

    def add_publisher(self, publisher: EventPublisher) -> None:
        self._publishers.append(publisher)

    async def publish(self, events: List[Event]) -> None:
        for publisher in self._publishers:
            await publisher.publish(events)
