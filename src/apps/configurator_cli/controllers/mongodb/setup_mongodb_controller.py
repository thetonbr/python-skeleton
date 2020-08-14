from typing import final, Dict, Any

from src.apps.configurator_cli.controllers.controller import BaseController
from src.libs.configurator.mongodb.configurer import MongoDBConfigurerService


@final
class SetupMongoDBController(BaseController):
    __slots__ = '_service'

    def __init__(self, service: MongoDBConfigurerService):
        self._service = service

    async def __call__(self, args: Dict[str, Any]) -> int:
        await self._service.setup(only_database=None, db_suffix=None)
        return 0
