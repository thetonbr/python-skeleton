from typing import List, final

from aioddd import EventPublisher, Event

from src.libs.shared.infrastructure.amqp_event_publisher import AMQPEventPublisher
from src.libs.shared.infrastructure.mongodb_event_publisher import MongoDBEventPublisher


@final
class EventPublisherDecorator(EventPublisher):
    __slots__ = ('_amqp', '_mongodb')

    def __init__(self, amqp: AMQPEventPublisher, mongodb: MongoDBEventPublisher) -> None:
        self._amqp = amqp
        self._mongodb = mongodb

    async def publish(self, events: List[Event]) -> None:
        await self._mongodb.publish(events)
        await self._amqp.publish(events)
