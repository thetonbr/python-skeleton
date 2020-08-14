from functools import reduce
from operator import iconcat
from typing import Tuple, NamedTuple, final, Optional, List, Dict, Any


class Exchange(NamedTuple):
    name: str
    type: str
    durable: bool


class Queue(NamedTuple):
    name: str
    durable: bool
    arguments: Optional[Dict[str, Any]]


class QueueBinding(NamedTuple):
    queue: str
    exchange: str
    routing_key: str
    arguments: Optional[Dict[str, Any]]


class AMQPServiceConfigData(NamedTuple):
    exchange: str  # base exchange
    queues_and_internal_queues_binds: List[str]  # base queues
    external_queues_binds: List[Tuple[str, str, str]]  # queue, external exchange, external routing key


@final
class AMQPServiceConfig:
    _exchanges: List[Exchange]
    _queues: List[Queue]
    _queues_binds: List[QueueBinding]

    def __init__(self, config: AMQPServiceConfigData):
        self._exchanges = self._compute_internal_exchanges(config.exchange)
        self._queues = self._compute_internal_queues(self._exchanges, config.queues_and_internal_queues_binds)
        internal_queues_binds = self._compute_internal_queues_binds(
            self._exchanges,
            config.queues_and_internal_queues_binds
        )
        external_queues_binds = self._compute_external_queues_binds(self._exchanges, config.external_queues_binds)
        self._queues_binds = internal_queues_binds + external_queues_binds

    def exchanges(self) -> List[Exchange]:
        return self._exchanges

    def queues(self) -> List[Queue]:
        return self._queues

    def queues_binds(self) -> List[QueueBinding]:
        return self._queues_binds

    @staticmethod
    def _compute_internal_exchanges(exchange: str) -> List[Exchange]:
        return [
            Exchange(name=exchange, type='direct', durable=True),
            Exchange(name=f'delayed.{exchange}', type='direct', durable=True),
            Exchange(name=f'graveyard.{exchange}', type='topic', durable=True),
        ]

    @staticmethod
    def _compute_internal_queues(exchanges: List[Exchange], queues: List[str]) -> List[Queue]:
        return reduce(iconcat, [
            [
                Queue(
                    name=f'{exchanges[0].name}.{queue}',
                    durable=True,
                    arguments={
                        'x-dead-letter-exchange': exchanges[1].name,
                        'x-dead-letter-routing-key': f'dead.{exchanges[0].name}.{queue}',
                        'x-message-ttl': 10000,
                    }
                ),
                Queue(
                    name=f'dead.{exchanges[0].name}.{queue}',
                    durable=True,
                    arguments={
                        'x-dead-letter-exchange': exchanges[0].name,
                        'x-dead-letter-routing-key': f'retry.{exchanges[0].name}.{queue}',
                        'x-message-ttl': 10000,
                    }
                ),
                Queue(
                    name=f'{exchanges[2].name}.{queue}',
                    durable=True,
                    arguments={
                        'x-message-ttl': 10000,
                    }
                )
            ]
            for queue in queues
        ], [])

    @staticmethod
    def _compute_internal_queues_binds(exchanges: List[Exchange], queues_binds: List[str]) -> List[QueueBinding]:
        return reduce(iconcat, [
            [
                QueueBinding(
                    queue=f'{exchanges[0].name}.{queue_bind}',
                    exchange=exchanges[0].name,
                    routing_key=queue_bind,
                    arguments=None
                ),
                QueueBinding(
                    queue=f'{exchanges[0].name}.{queue_bind}',
                    exchange=exchanges[0].name,
                    routing_key=f'retry.{exchanges[0].name}.{queue_bind}',
                    arguments=None
                ),
                QueueBinding(
                    queue=f'dead.{exchanges[0].name}.{queue_bind}',
                    exchange=exchanges[1].name,
                    routing_key=f'dead.{exchanges[0].name}.{queue_bind}',
                    arguments=None
                ),
                QueueBinding(
                    queue=f'{exchanges[0].name}.{queue_bind}',
                    exchange=exchanges[2].name,
                    routing_key=queue_bind,
                    arguments=None
                )
            ]
            for queue_bind in queues_binds
        ], [])

    @staticmethod
    def _compute_external_queues_binds(
            exchanges: List[Exchange],
            queues_binds: List[Tuple[str, str, str]]
    ) -> List[QueueBinding]:
        return reduce(iconcat, [
            [
                QueueBinding(
                    queue=f'{exchanges[0].name}.{queue_bind[0]}',
                    exchange=queue_bind[1],
                    routing_key=queue_bind[2],
                    arguments=None
                )
            ]
            for queue_bind in queues_binds
        ], [])
