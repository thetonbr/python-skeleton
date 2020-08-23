import traceback
from abc import ABC, abstractmethod
from logging import Logger
from traceback import print_tb
from typing import Optional, Dict, Any

from aioddd import Event, EventMapper, CommandBus
from aiormq import ChannelNotFoundEntity, ChannelAccessRefused, ChannelLockedResource

from src.libs.shared.infrastructure.amqp_event_consumer import AMQPEventConsumer, AMQPResponder


class BaseController:
    @abstractmethod
    async def __call__(self, args: Dict[str, Any]) -> int:
        pass


class BaseConsumerController(ABC, BaseController):
    __slots__ = ('_queue_name', '_logger', '_consumer', '_command_bus', '_retries', '_consumed', '_processed', '_stop')

    def __init__(
            self,
            event_mapper: EventMapper,
            logger: Logger,
            consumer: AMQPEventConsumer,
            command_bus: CommandBus,
            retries: int,
    ) -> None:
        self._queue_name = f'{event_mapper.service_name()}.{event_mapper.name()}'
        self._logger = logger
        self._consumer = consumer
        self._command_bus = command_bus
        self._retries = retries
        self._consumed = 0
        self._processed = 0
        self._stop = False

    async def __call__(self, args: Dict[str, Any]) -> int:
        self._logger.info({'message': f'Consuming {self._queue_name}...'})
        try:
            self._retries = int(self._retries if args.get('retries') is None else args.get('retries'))
            self._stop = bool(args.get('stop', self._stop))
            await self._consumer.consume(self._queue_name, int(args.get('times', 0)), self._callback)
        except (ChannelAccessRefused, ChannelNotFoundEntity, ChannelLockedResource) as err:
            self._logger.info({'message': f'AMQP Channel not available error {str(type(err))}: {str(err)}'})
            print_tb(err.__traceback__)
            self._logger.info({'message': f'Total processed: {self._processed}'})
            self._logger.info({'message': f'Total consumed: {self._consumed}'})
            return 1
        except Exception as err:
            self._logger.info(traceback.format_exc())
            self._logger.info({'message': f'Unhandled error {str(type(err))}: {str(err)}'})
            self._logger.info({'message': f'Total processed: {self._processed}'})
            self._logger.info({'message': f'Total consumed: {self._consumed}'})
        return int(self._consumed != self._processed)

    @abstractmethod
    async def _on_error(self, err: Exception, event: Event, responder: AMQPResponder) -> Optional[Exception]:
        pass

    @abstractmethod
    async def _on_event(self, event: Event) -> None:
        pass

    async def _callback(self, event: Event, responder: AMQPResponder) -> None:
        self._consumed += 1
        try:
            await self._on_event(event)
            responder.ack()
            self._processed += 1
            self._logger.info({'message': 'Processed'})
        except Exception as err:
            error = await self._on_error(err, event, responder)
            if not error:
                self._logger.info({'message': 'Consumed'})
                return
            self._logger.info({'message': f'Retries: {responder.retries()}/{self._retries}'})
            if responder.retries() < self._retries:
                self._consumed -= 1
                responder.reject()
                self._logger.info({'message': 'Retrying...'})
            else:
                print_tb(err.__traceback__)
                if not self._stop:
                    self._processed += 1
                await responder.graveyard()
                self._logger.info({'message': 'Unprocessed'})
