from json import dumps
from typing import List

import aio_pika

from aioddd import EventPublisher, Event, EventMapper, find_event_mapper_by_type


class AMQPEventPublisher(EventPublisher):
    __slots__ = ('_connection', '_mappers', '_exchange')

    def __init__(self, connection: aio_pika.Connection, mappers: List[EventMapper], exchange: str) -> None:
        self._connection = connection
        self._mappers = mappers
        self._exchange = exchange

    async def publish(self, events: List[Event]) -> None:
        async with self._connection.channel() as channel:
            _ = [await self._publish(channel, event) for event in events]

    async def _publish(self, channel: aio_pika.Channel, event: Event) -> None:
        mapper = find_event_mapper_by_type(event, self._mappers)
        exchange = await channel.get_exchange(name=self._exchange)
        await exchange.publish(
            message=aio_pika.Message(
                body=dumps(mapper.encode(event)).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type='application/json',
                message_id=str(event.get_meta()['id'])
            ),
            routing_key=mapper.name(),
        )
