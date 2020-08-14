from json import loads
from typing import List, Callable, Awaitable, Any, Optional

import aio_pika
from aio_pika import IncomingMessage, Connection
from aio_pika.exceptions import QueueEmpty

from aioddd import Event, EventMapper, find_event_mapper_by_name
from src.libs.shared.infrastructure.amqp_event_publisher import AMQPEventPublisher


class AMQPResponder:
    _dead_publisher: AMQPEventPublisher
    _message: IncomingMessage
    _event: Event
    _delivered: bool

    def __init__(self, dead_publisher: AMQPEventPublisher, message: IncomingMessage, event: Event) -> None:
        self._dead_publisher = dead_publisher
        self._message = message
        self._event = event
        self._delivered = False

    def ack(self) -> None:
        if not self._delivered:
            self._message.ack()
            self._delivered = True

    def nack(self) -> None:
        if not self._delivered:
            self._message.nack()
            self._delivered = True

    def reject(self, requeue: bool = False) -> None:
        if not self._delivered:
            self._message.reject(requeue)
            self._delivered = True

    def retries(self) -> int:
        headers = self._message.properties.headers or dict()
        if 'x-death' in headers and len(headers['x-death']) > 1 and 'count' in headers['x-death'][0]:
            return int(headers['x-death'][0]['count'])
        return 0

    async def graveyard(self) -> None:
        if not self._delivered:
            await self._dead_publisher.publish([self._event])
            self.ack()


class AMQPEventConsumer:
    __slots__ = ('_connection', '_mappers', '_dead_publisher', '_channel')

    def __init__(self, connection: Connection, mappers: List[EventMapper], dead_publisher: AMQPEventPublisher) -> None:
        self._connection = connection
        self._mappers = mappers
        self._dead_publisher = dead_publisher
        self._channel = None  # type: Optional[aio_pika.channel.Channel]

    async def consume(
            self,
            queue_name: str,
            times: int,
            callback: Callable[[Event, AMQPResponder], Awaitable[None]]
    ) -> None:
        if times < 0:
            return
        async with self._connection.channel() as channel:
            self._channel = channel
            if not self._channel:
                return
            await self._channel.set_qos(prefetch_count=1)
            queue = await self._channel.get_queue(name=queue_name)
            try:
                async with queue.iterator() as queue_iter:
                    always_repeat = times == 0
                    async for msg in queue_iter:
                        async with msg.process(ignore_processed=True):
                            await self._on_message_callback(msg, callback)
                            if not always_repeat:
                                times -= 1
                                if times == 0:
                                    break

            except QueueEmpty:
                pass

    async def _on_message_callback(self, msg: IncomingMessage, callback: Callable[[Event, AMQPResponder], Any]) -> None:
        event = self._decode_event_from_message(msg.body)
        await callback(event, AMQPResponder(self._dead_publisher, msg, event))

    def _decode_event_from_message(self, body: bytes) -> Event:
        message = loads(body.decode('utf-8'))
        name = message['meta']['message']
        mapper = find_event_mapper_by_name(name=name, mappers=self._mappers)
        return mapper.decode(message['attributes'])
