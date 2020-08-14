from typing import final, Dict, Any

from src.apps.configurator_cli.controllers.controller import BaseController
from src.libs.configurator.amqp.configurer import AMQPConfigurerService


@final
class SetupAMQPController(BaseController):
    __slots__ = '_service'

    def __init__(self, service: AMQPConfigurerService):
        self._service = service

    async def __call__(self, args: Dict[str, Any]) -> int:
        await self._service.setup(only_exchange=None, exchange_suffix=None)
        return 0
