from functools import reduce
from logging import Logger
from operator import iconcat
from typing import final, List, Optional

from aio_pika import Connection

from src.libs.configurator.amqp.config import AMQPServiceConfig, Exchange, Queue, QueueBinding


@final
class AMQPConfigurerService:
    __slots__ = ('_connection', '_configs', '_logger')

    def __init__(self, connection: Connection, configs: List[AMQPServiceConfig], logger: Logger):
        self._connection = connection
        self._configs = configs
        self._logger = logger

    async def setup(self, only_exchange: Optional[str] = None, exchange_suffix: Optional[str] = None) -> None:
        self._logger.info({'message': 'Setting AMQP…'})
        configs = self._prepare_configs(only_exchange, exchange_suffix)
        async with self._connection.channel() as channel:
            exchanges: List[Exchange] = reduce(iconcat, [config.exchanges() for config in configs], [])
            _ = [
                await channel.declare_exchange(
                    name=e.name,
                    type=e.type,
                    durable=e.durable
                )
                for e in exchanges
            ]
            queues: List[Queue] = reduce(iconcat, [config.queues() for config in configs], [])
            _ = [
                await channel.declare_queue(
                    name=q.name,
                    durable=q.durable,
                    arguments=q.arguments
                )
                for q in queues
            ]
            queues_binds: List[QueueBinding] = reduce(iconcat, [config.queues_binds() for config in configs], [])
            _ = [
                await (await channel.get_queue(name=qb.queue)).bind(
                    exchange=qb.exchange,
                    routing_key=qb.routing_key,
                    arguments=qb.arguments
                )
                for qb in queues_binds
            ]
        self._logger.info({'message': 'Finished!'})

    async def clean(self, only_exchange: Optional[str] = None, exchange_suffix: Optional[str] = None) -> None:
        self._logger.info({'message': 'Cleaning AMQP…'})
        configs = self._prepare_configs(only_exchange, exchange_suffix)
        async with self._connection.channel() as channel:
            queues_binds: List[QueueBinding] = reduce(iconcat, [config.queues_binds() for config in configs], [])
            _ = [
                await (await channel.get_queue(name=qb.queue)).unbind(
                    exchange=qb.exchange,
                    routing_key=qb.routing_key,
                )
                for qb in queues_binds
            ]
            queues: List[Queue] = reduce(iconcat, [config.queues() for config in configs], [])
            _ = [
                await channel.queue_delete(
                    queue_name=q.name,
                    if_unused=False, if_empty=False
                )
                for q in queues
            ]
            exchanges: List[Exchange] = reduce(iconcat, [config.exchanges() for config in configs], [])
            _ = [
                await channel.exchange_delete(
                    exchange_name=e.name,
                    if_unused=False
                )
                for e in exchanges
            ]
        self._logger.info({'message': 'Cleaned!'})

    def _prepare_configs(
            self,
            only_exchange: Optional[str],
            exchange_suffix: Optional[str]
    ) -> List[AMQPServiceConfig]:
        configs = self._configs if not only_exchange else \
            [config for config in self._configs if config.exchanges()[0].name == only_exchange]
        for i, config in enumerate(configs):
            if exchange_suffix:
                real_exchanges = configs[i].exchanges()
                exchanges = []
                for exchange in real_exchanges:
                    exchanges.append(Exchange(
                        name=f'{exchange.name}{exchange_suffix}',
                        type=exchange.type,
                        durable=exchange.durable,
                    ))
                configs[i].exchanges = lambda: exchanges  # type: ignore

        return configs
